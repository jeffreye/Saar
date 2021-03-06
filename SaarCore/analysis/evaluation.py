from analysis.indicator import *
from enum import IntEnum
from datetime import *
from pandas import *
import math
import threading
from analysis.technical_analysis import last_business_day
from data.stock import stock_state
import csv
from data.evaluation import evaluation_result

class evaluator(object):
    """evaluator of scheme"""

    def __init__(self,scheme, session_commit = None, log = False):
        assert scheme.evaluation_end > scheme.evaluation_start
        self.scheme = scheme
        self.from_date = scheme.evaluation_start
        self.to_date = scheme.evaluation_end

        self.prefetch_days = 100
        '''fetech more dates to calculate indicators'''

        self.money_remains = 0
        '''money in pocket for every stock'''

        self.stock_profit_count = 0

        self.stock_loss_count = 0

        self.indicator = self.scheme.combine_indicators()

        self.log = log

        self.set_listener(None,None,None)

    def set_listener(self,on_start,on_manipulated,on_done):
        self.on_start = on_start
        self.on_manipulated = on_manipulated
        self.on_done = on_done


    def calculate(self):
        '''calculate scheme's win rate'''
        #buy and sell simulatively(range:all stocks)
        if len(self.scheme.indicators) == 0:
            self.scheme.evaluation_result = evaluation_result(scheme_id = self.scheme.id,progress = 1,money = 0,win_rate = 0,money_used = 0)
            return 0,0

        self.scheme.evaluation_result = evaluation_result(scheme_id = self.scheme.id,progress = 0,money = 0,win_rate = 0)
        if self.on_start != None:
            self.on_start(self.scheme.evaluation_result)
        with open('evaluation%s.csv' % self.scheme.name, 'w+') as self.csvfile:
            self.writer = csv.DictWriter(self.csvfile,delimiter=',',fieldnames = ['date','operation','code','price','numbers','money_remains'])
            self.writer.writeheader()
            self.csvfile.flush()
            for i,stock in enumerate(self.scheme.stocks):
                profit,loss,money = self.manipulate_stock(stock)
                self.stock_profit_count += profit
                self.stock_loss_count += loss
                self.money_remains += money

                self.scheme.evaluation_result.progress = (i+1)/len(threads)
                profit_rate = 0 if (self.stock_profit_count + self.stock_loss_count) == 0 else self.stock_profit_count / (self.stock_profit_count + self.stock_loss_count)
                self.scheme.evaluation_result.money = self.money_remains
                self.scheme.evaluation_result.money_used = self.scheme.total_money * (i + 1)
                self.scheme.evaluation_result.win_rate = profit_rate

                if self.on_manipulated != None:
                    self.on_manipulated(self.scheme.evaluation_result)


        self.scheme.start_evaluation = False
        if self.on_done != None:
            self.on_done(self.scheme.evaluation_result)

        return profit_rate,self.money_remains

    def manipulate_stock(self,stock):
        #prepare data
        if not stock.pull_data(self.from_date - timedelta(days = self.prefetch_days),self.to_date):
            return 0,0,0
        
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
        for day in bdate_range(start = self.from_date,end = self.to_date):
            if day not in stock.prices.index:
                continue
            signal = self.indicator.get_signal(stock,day)
            if stock.state == stock_state.close_position and signal.can_buy:
                #invest it and calculate money remains
                if self.buy(stock,day):
                    stock.state = stock_state.open_position
            elif stock.state == stock_state.open_position and ( signal.can_buy or self.should_buy_remains(stock,day) ):
                if self.buy(stock,day):
                    stock.state = stock_state.hold_position
            elif stock.state == stock_state.hold_position and ( signal.can_sell or self.should_sell(stock,day) ):
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
            elif stock.state == stock_state.open_position and ( signal.can_sell or self.should_sell_remains(stock,day)):
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
            sell_num -= sell_num % 100
            if sell_num < 100:
                sell_num = stock.holding_stocks
        else:
            sell_num = stock.holding_stocks
            
        stock.holding_stocks -= sell_num
        stock.money_remains += sell_num * price
        stock.last_operate_date = day
        if self.log:
            print('sells %s (%f * %d) at %s , money remains %d' % (stock.code,price,sell_num,day,stock.money_remains))
            self.writer.writerow({'date':day.isoformat(),'operation':'sell','code':stock.code,'price':price,'numbers':sell_num,'money_remains':stock.money_remains})
            self.csvfile.flush()

    def buy(self,stock,day):
        '''invest it and calculate money remains'''
        price = stock.prices.Close[day]
        if stock.money_remains < price:
            return False
        elif stock.state == stock_state.open_position or stock.state == stock_state.hold_position:
            invest_money =  stock.money_remains
        else:
            stock.buy_date = day
            invest_money = math.floor(self.scheme.first_investment_percent * stock.money_remains)
            #stock.last_operate_date = day

        stock.last_operate_date = day
        num = math.floor( invest_money / price ) 
        num -= num % 100
        if num < 100:
            return False
        stock.holding_stocks += num
        stock.money_remains -= price * num
        if self.log:
            print('buys %s (%f * %d) at %s , money remains %d' % (stock.code,price,num,day,stock.money_remains))
            self.writer.writerow({'date':day.isoformat(),'operation':'buy','code':stock.code,'price':price,'numbers':num,'money_remains':stock.money_remains})
            self.csvfile.flush()
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

    def __init__(self, scheme, session_commit = None,log = False):
        super().__init__(scheme,session_commit, log)
        self.counter_lock = threading.Lock()

    
    def calculate(self):
        '''calculate scheme's win rate'''
        #buy and sell simulatively(range:all stocks)

        if len(self.scheme.indicators) == 0:
            self.scheme.evaluation_result = evaluation_result(scheme_id = self.scheme.id,progress = 1,money = 0,win_rate = 0,money_used = 0)
            return 0,0

        threads = []

        for stock in self.scheme.stocks:
            t = threading.Thread(target = self._manipulate_stock_threading, args = (stock,), name = 'manipulate ' + stock.code)
            t.start()
            threads.append(t)
           
        self.scheme.evaluation_result = evaluation_result(scheme_id = self.scheme.id,progress = 0,money = 0,money_used = 0,win_rate = 0)
        if self.on_start != None:
            self.on_start(self.scheme.evaluation_result)

        for i,t in enumerate(threads):
            t.join()
            self.scheme.evaluation_result.progress = (i+1)/len(threads)
            profit_rate = 0 if (self.stock_profit_count + self.stock_loss_count) == 0 else self.stock_profit_count / (self.stock_profit_count + self.stock_loss_count)
            self.scheme.evaluation_result.money = self.money_remains
            self.scheme.evaluation_result.money_used = self.scheme.total_money * (i + 1)
            self.scheme.evaluation_result.win_rate = profit_rate

            if self.on_manipulated != None:
                self.on_manipulated(self.scheme.evaluation_result)


        self.scheme.start_evaluation = False
        if self.on_done != None:
            self.on_done(self.scheme.evaluation_result)

        return profit_rate,self.money_remains

        return profit_rate,sum(self.money_remains.values())

    def _manipulate_stock_threading(self, stock):

        profit,loss,money = self.manipulate_stock(stock)

        self.counter_lock.acquire()
        self.stock_profit_count += profit
        self.stock_loss_count += loss
        self.money_remains += money
        self.counter_lock.release()