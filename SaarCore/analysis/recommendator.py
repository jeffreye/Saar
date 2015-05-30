from analysis.evaluation import stock_state
from analysis.indicator import *
from data.stock import all_stocks
from data.recommendation import *
from datetime import *

class recommendator(object):
    """recommendator of stocks"""
    #TODO

    def __init__(self,scheme):
        self.scheme = scheme
        self.indicator = self.scheme.combine_indicators()

    def get_daliy_stocks(self, date = datetime.now().date()):
        '''recommend stocks base on user's scheme'''
        for s in all_stocks():
            self.manipulate_stock(s,date)
            
    def manipulate_stock(self,stock,day):
        '''Determine stock should be operated'''
        if day not in stock.prices.index:
            return False
        if stock.code in self.scheme.recommend_stocks:
            data = self.scheme.recommend_stocks[stock.code]
            stock.last_operation_date = data.last_operation_date
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
                                                                          stock_code = stock.code,
                                                                          stock_name = stock.name,
                                                                          operation = recommendation_operation.buy,
                                                                          state = stock_state.close_position)
        elif stock.state == stock_state.open_position and ( signal.can_buy or self.should_buy_remains(stock,day) ):
            if self.buy(stock,day):
                self.scheme.recommend_stocks[stock.code].operation =  recommendation_operation.buy
        elif stock.state == stock_state.hold_position and ( signal.can_sell or self.should_sell(stock,day) ):
            #sell it and money comes back
            self.sell(stock,day)
            self.scheme.recommend_stocks[stock.code].operation =  recommendation_operation.sell
        elif stock.state == stock_state.open_position and ( signal.can_sell or self.should_sell_remains(stock,day)):
            #sell remains and all money comes back
            self.sell(stock,day)
            self.scheme.recommend_stocks[stock.code].operation =  recommendation_operation.sell
            del stock.last_operation_date
        else:
            pass


        del stock.state


    def sell(self,stock,day, all = False):
        '''sell it and money comes back'''
        assert stock.state != stock_state.close_position

        price = stock.prices.Close[day]
                    
        stock.last_operate_date = day
        if self.log:
            print('sells %s (%f * %d) at %s , money remains %d' % (stock.code,price,sell_num,day,stock.money_remains))

    def buy(self,stock,day):
        '''invest it and calculate money remains'''
        price = stock.prices.Close[day]
        stock.last_operate_date = day
        if self.log:
            print('buys %s (%f * %d) at %s , money remains %d' % (stock.code,price,num,day,stock.money_remains))
        return True

    def should_buy_remains(self,stock,day):
        '''if stock's price hit the profit limit or loss limit'''
        assert stock.state == stock_state.open_position
        if day == stock.prices.index[0]:
            return False

        buy_price = stock.prices.Close[self.get_last_operate_date(stock)]
        profit = (stock.prices.Close[day] - buy_price)/buy_price 
        return profit >= self.scheme.additional_investment_condition

    def should_sell(self,stock,day):
        '''if stock's price hit the profit limit or loss limit'''
        assert stock.state != stock_state.close_position
        
        if (day - stock.buy_date).days >= self.scheme.holding_cycles:
            return True
        
        price = stock.prices.Close[day]
        buy_price = stock.prices.Close[self.get_last_operate_date(stock)]
        profit = (price - buy_price ) / buy_price
        return profit >= self.scheme.profit_limit or profit <= -self.scheme.loss_limit

    def should_sell_remains(self,stock,day):
        '''if stock's price hit the additional_investment condition'''
        assert stock.state != stock_state.close_position
        
        if self.should_sell(stock,day):
            return True
        
        price = stock.prices.Close[day]
        buy_price = stock.prices.Close[self.get_last_operate_date(stock)]
        loss = -(price - buy_price ) / buy_price
        return loss >= self.scheme.additional_investment_condition
