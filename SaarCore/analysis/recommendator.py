from analysis.indicator import *
from data.stock import all_stocks, stock_state
from data.recommendation import *
from datetime import *
import threading

class recommendator(object):
    """recommendator of stocks"""

    def __init__(self,scheme, log = False):
        self.scheme = scheme
        self.prefetch_days = 100
        self.indicator = self.scheme.combine_indicators()
        self.log = log

    def get_daliy_stocks(self, date = today()):
        '''recommend stocks base on user's scheme'''

        threads = []
        for s in all_stocks():
            t = threading.Thread(target = self.manipulate_stock, args = (s,date), name = 'manipulate ' + s.code)
            t.start()
            threads.append(t)
           
        for i,t in enumerate(threads):
            t.join()
            
            
    def manipulate_stock(self,stock,day):
        '''Determine stock should be operated'''
        
        if not stock.pull_data(day - timedelta(days = self.prefetch_days),day):
            return False

        if day not in stock.prices.index:
            print('The day is not in stock prices')
            return False

        if stock.code in self.scheme.recommend_stocks:       
            data = self.scheme.recommend_stocks[stock.code]     
            print(data)
            stock.last_operate_date = data.last_operation_date
            stock.buy_date = data.buy_date
            stock.state = data.state
        else:
            stock.state =  stock_state.close_position

        self.indicator.precompute(stock)
        signal = self.indicator.get_signal(stock,day)
        if stock.state == stock_state.close_position and signal.can_buy:
            #invest it and calculate money remains
            if self.buy(stock,day):
                self.scheme.recommend_stocks[stock.code] = recommendation(scheme_id = self.scheme.id,
                                                                          buy_date = day,
                                                                          last_operation_date = day,
                                                                          recommendation_operation_date = day,
                                                                          stock_code = stock.code,
                                                                          stock_name = stock.name,
                                                                          operation = recommendation_operation.buy,
                                                                          state = stock_state.close_position)
                
            del stock.state
            return True
        elif stock.state == stock_state.open_position and ( signal.can_buy or self.should_buy_remains(stock,day) ):
            if self.buy(stock,day):
                data.operation =  recommendation_operation.buy
                data.recommendation_operation_date =  day
            del stock.last_operate_date
            del stock.buy_date
            del stock.state
            return True
        elif stock.state == stock_state.hold_position and ( signal.can_sell or self.should_sell(stock,day) ):
            #sell it and money comes back
            self.sell(stock,day)
            self.scheme.recommend_stocks[stock.code].operation =  recommendation_operation.sell
            data.recommendation_operation_date =  day
            del stock.last_operate_date
            del stock.buy_date
            del stock.state
            return True
        elif stock.state == stock_state.open_position and ( signal.can_sell or self.should_sell_remains(stock,day)):
            #sell remains and all money comes back
            self.sell(stock,day)
            self.scheme.recommend_stocks[stock.code].operation =  recommendation_operation.sell
            data.recommendation_operation_date =  day
            del stock.last_operate_date
            del stock.buy_date
            del stock.state
            return True
        else:
            pass

        return False

    def sell(self,stock,day, all = False):
        '''sell it and money comes back'''
        assert stock.state != stock_state.close_position

        price = stock.prices.Close[day]
                    
        stock.last_operate_date = day
        if self.log:
            print('sells %s (%f) at %s ' % (stock.code,price,day))

    def buy(self,stock,day):
        '''invest it and calculate money remains'''
        price = stock.prices.Close[day]
        stock.last_operate_date = day
        if self.log:
            print('buys %s (%f) at %s' % (stock.code,price,day))
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
