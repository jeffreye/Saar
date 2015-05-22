from analysis.indicator import *
from enum import Enum
from datetime import *
from pandas import *
import math
import threading
from analysis.technical_analysis import last_business_day

class stock_state(Enum):
    wait = 0

    open_position = 1
    '''bought just now'''

    hold_position = 2

    sell_half = 1

    close_position = 0


class evaluator(object):
    """evaluator of scheme"""

    def __init__(self,scheme,from_date,to_date , log = False):
        assert to_date > from_date
        self.scheme = scheme
        self.from_date = from_date
        self.to_date = to_date

        self.prefetch_days = 100
        '''fetech more dates to calculate indicators'''

        

        self.holding_stocks = {}
        '''key value pair - stock and invest money'''

        self.money_remains = {}
        '''money in pocket for every stock'''

        self.stock_profit_count = {}

        self.stock_loss_count = {}

        self.buy_dates = {}

        self.indicator = self.scheme.combine_indicators()

        self.log = log


    def calculate(self):
        '''calculate scheme's win rate'''
        #buy and sell simulatively(range:all stocks)
        

        for stock in self.scheme.stocks:
            self.stock_profit_count[stock], self.stock_loss_count[stock],self.money_remains[stock] = self.manipulate_stock(stock)
           
        profits = sum(self.stock_profit_count.values())
        losses = sum(self.stock_loss_count.values())
        profit_rate = 0 if (profits + losses) == 0 else profits / (profits + losses)
        return profit_rate,sum(self.money_remains.values())

    def manipulate_stock(self,stock):
        #prepare data
        if not stock.pull_data(self.from_date - timedelta(days = self.prefetch_days),self.to_date):
            return 0,0
        
        last_money_remains = self.scheme.total_money
        stock.money_remains = last_money_remains
        stock.state = stock_state.wait
        stock.holding_stocks = 0
        #stock.last_operate_date
        #stock.buy_date
        stock_profit_count = 0
        stock_loss_count = 0

        self.indicator.precompute(stock)
            
        #monitoring stock and invest it
        for day in bdate_range(start = self.from_date,end = self.to_date, freq = 'D'):
            if day not in stock.prices.index:
                continue
            signal = self.indicator.get_signal(stock,day)
            if stock.state == stock_state.close_position and signal == indicator_signal.buy :
                #invest it and calculate money remains
                if self.buy(stock,day):
                    stock.state = stock_state.open_position
            elif stock.state == stock_state.open_position and ( signal == indicator_signal.buy or self.should_buy_remains(stock,day) ):
                if self.buy(stock,day):
                    stock.state = stock_state.hold_position
            elif stock.state == stock_state.hold_position and ( signal == indicator_signal.sell or self.should_sell(stock,day) ):
                #sell it and money comes back
                self.sell(stock,day)

                if stock.holding_stocks > 0:
                    stock.state = stock_state.open_position
                else:                    
                    stock.state = stock_state.close_position

                    if stock.money_remains >= last_money_remains:
                        stock_profit_count+=1
                    else:
                        stock_loss_count+=1
                    last_money_remains = stock.money_remains
            elif stock.state == stock_state.open_position and ( signal == indicator_signal.sell or self.should_sell_remains(stock,day)):
                #sell remains and all money comes back
                self.sell(stock,day)
                stock.state = stock_state.close_position

                if stock.money_remains >= last_money_remains:
                    stock_profit_count+=1
                else:
                    stock_loss_count+=1
                last_money_remains = stock.money_remains
            else:
                pass

        #finally comes to deadline
        if stock.state != stock_state.close_position:
            self.sell(stock,stock.prices.index[-1],all = True)
            if stock.money_remains >= last_money_remains:
                stock_profit_count+=1
            else:
                stock_loss_count+=1
            last_money_remains = stock.money_remains

        del stock.money_remains
        del stock.state
        del stock.holding_stocks
        if stock_profit_count > 0 or stock_loss_count > 0:   
            del stock.last_operate_date
            del stock.buy_date
        return stock_profit_count,stock_loss_count,last_money_remains

    def sell(self,stock,day, all = False):
        '''sell it and money comes back'''
        assert stock.state != stock_state.close_position

        price = stock.prices.Close[day]

        if stock.state == stock_state.hold_position and not all:
            sell_num = math.floor(stock.holding_stocks * self.scheme.first_investment_percent)
            if sell_num < 100:
                sell_num = stock.holding_stocks
            stock.holding_stocks -= sell_num
            stock.money_remains += sell_num * price
        else:
            stock.money_remains += stock.holding_stocks * price
            stock.holding_stocks = 0
            
        stock.last_operate_date = day
        if self.log:
            print('sells %s (%f) at %s , money remains %d' % (stock.code,price,day,stock.money_remains))

    def buy(self,stock,day):
        '''invest it and calculate money remains'''
        price = stock.prices.Close[day]
        if stock.money_remains < price:
            return
        elif stock.state == stock_state.open_position or stock.state == stock_state.hold_position:
            invest_money =  stock.money_remains
        else:
            stock.buy_date = day
            invest_money = self.scheme.first_investment_percent * stock.money_remains
            #stock.last_operate_date = day

        stock.last_operate_date = day
        num = math.floor( invest_money / price )
        if num < 100:
            return False
        stock.holding_stocks += num
        stock.money_remains -= price * num
        if self.log:
            print('buys %s (%f) at %s , money remains %d' % (stock.code,price,day,stock.money_remains))
        return True

    def should_buy_remains(self,stock,day):
        '''if stock's price hit the profit limit or loss limit'''
        assert stock.state == stock_state.open_position
        if day == stock.prices.index[0]:
            return False

        buy_price = stock.prices.Close[stock.last_operate_date]
        profit = (stock.prices.Close[day] - buy_price)/buy_price 
        return profit >= self.scheme.additional_investment_condition

    def should_sell(self,stock,day):
        '''if stock's price hit the profit limit or loss limit'''
        assert stock.state != stock_state.close_position
        
        if (day - stock.buy_date).days >= self.scheme.holding_cycles:
            return True
        
        price = stock.prices.Close[day]
        buy_price = stock.prices.Close[stock.last_operate_date]
        profit = (price - buy_price ) / buy_price
        return profit >= self.scheme.profit_limit or profit <= -self.scheme.loss_limit

    def should_sell_remains(self,stock,day):
        '''if stock's price hit the additional_investment condition'''
        assert stock.state != stock_state.close_position
        
        if self.should_sell(stock,day):
            return True
        
        price = stock.prices.Close[day]
        buy_price = stock.prices.Close[stock.last_operate_date]
        loss = -(price - buy_price ) / buy_price
        return loss >= self.scheme.additional_investment_condition

    def get_results_csv(self):
        '''returns a .csv ( *Date *Stock *BUY/SELL *Profit/Loss ) if calculation is done'''
        pass



class parallel_evaluator(evaluator):
    """description of class"""

    def __init__(self, scheme, from_date, to_date):
        super().__init__(scheme, from_date, to_date)
        self.counter_lock = threading.Lock()

    
    def calculate(self):
        '''calculate scheme's win rate'''
        #buy and sell simulatively(range:all stocks)
        
        threads = []

        for stock in self.scheme.stocks:
            t = threading.Thread(target = self._manipulate_stock_threading, args = (stock,), name = 'manipulate ' + stock.code)
            t.start()
            threads.append(t)
           
        for t in threads:
            t.join()

        profits = sum(self.stock_profit_count.values())
        losses = sum(self.stock_loss_count.values())
        profit_rate = 0 if (profits + losses) == 0 else profits / (profits + losses)
        return profit_rate,sum(self.money_remains.values())

    def _manipulate_stock_threading(self, stock):

        profit,loss,money = self.manipulate_stock(stock)

        self.counter_lock.acquire()
        self.stock_profit_count[stock], self.stock_loss_count[stock],self.money_remains[stock] = profit,loss,money
        self.counter_lock.release()