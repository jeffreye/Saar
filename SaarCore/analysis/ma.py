from data.stock import stock
from analysis.indicator import *
from analysis.technical_analysis import *
from datetime import *

class ma(indicator_base):
    """description of class"""

    ma1 = 'MA*1'
    ma2 = 'MA*2'
    ma4 = 'MA*4'

    def __init__(self,parameter,description):
        self.days =  clamp(parameter.param1,description.param1_upper,description.param1_lower)

    def get_buy_dates(self,stock,from_date,to_date):
        pass

    def get_sell_dates(self,stock,from_date,to_date):
        pass

    def get_buy_and_sell_dates(self,stock,from_date,to_date):
        pass

    def get_signal(self,stock,date):
        '''BUY or SELL'''
        #if data is not enough , returns wait
        if stocks.prices.index.size == 0:
            raise BaseException('cannot retrieve stocks.prices')

        size = (stock.prices.index[0] - date).days
        if size < self.days:
            return indicator_signal.wait

        current_ma1 = stock.indicator_values[ma1][date] = sma(stock,date,self.days)
        current_ma2 = stock.indicator_values[ma2][date] = sma(stock,date,self.days*2)
        current_ma4 = stock.indicator_values[ma4][date] = sma(stock,date,self.days*4)

        if len(stock.indicator_values[ma_mark]) == 1:
            return indicator_signal.wait
        
        buy_cross = cross.try_identify(stock.indicator_values[ma2][date - 1],stock.indicator_values[ma4][date - 1]
                                              ,current_ma2,current_ma4)
        sell_cross = cross.try_identify(stock.indicator_values[ma][date - 1],stock.indicator_values[ma2][date - 1]
                                              ,current_ma,current_ma2)
        #if golden cross appears,returns buy
        if buy_cross == cross.golden:
            return indicator_signal.buy
        #if dead cross appears,returns sell        
        elif sell_cross == cross.dead:
            return indicator_signal.sell
        else:
            return indicator_signal.wait
        pass