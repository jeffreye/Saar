﻿from data.stock import stock
from analysis.indicator import *
from data.indicator import *
from datetime import *
from analysis.technical_analysis import *
from pandas.tseries.offsets import BDay
from pandas import Series

class macd(indicator_base):
    """MACD indicator"""

    dea = 'MACD_DEA'
    dif = 'MACD_DIF'

    def __init__(self,parameter = None,description = None):
            
        if parameter != None:
            assert parameter.params[0] <= parameter.params[1]
        else:
            parameter = indicator_parameter(9,25,6)

        if description == None:
            description = parameter.description

        if description != None:
            assert description.uppers[0] >= description.lowers[0]
            assert description.uppers[1] >= description.lowers[1]
            assert description.uppers[2] >= description.lowers[2]
        else:
            description = indicator_description('MACD',3,'lambda p : p[1] >= p[0] + 1 and  p[2] * 2 <= p[1]')
            description.buy_point = u'金叉'
            description.sell_point = u'死叉'
            #short
            description.lowers[0] = 2
            description.uppers[0] = 20
            description.steps[0] = 1
            #long
            description.lowers[1] = 3
            description.uppers[1] = 40
            description.steps[1] = 1
            #signal
            description.lowers[2] = 2
            description.uppers[2] = 10
            description.steps[2] = 1

        super(macd,self).__init__(parameter, description)
        
    @property
    def parameter(self):
        return self._parameter
    
    @parameter.setter
    def parameter(self,parameter):
        self._parameter = parameter
        if parameter != None:
            self.short =   clamp(parameter.params[0],self.description.lowers[0],self.description.uppers[0])
            self.long =    clamp(parameter.params[1],self.description.lowers[1],self.description.uppers[1])
            self.signal =  clamp(parameter.params[2],self.description.lowers[2],self.description.uppers[2])
        
    def precompute(self,stock):
        assert stock.prices.index.size > 0,'{0}\'s prices is empty'.format(stock.code)

        dif = ewma(stock.prices.Close,span = self.short) - ewma(stock.prices.Close,span = self.long)
        dea = ewma(dif,span = self.signal)

        #cache values
        stock.indicator_values[macd.dif]=dif
        stock.indicator_values[macd.dea]=dea

    def get_signal(self,stock,date):
        '''BUY or SELL'''
        assert stock.prices.index.size != 0
        
        #no data for now
        if date < stock.prices.index[0] or date not in stock.prices.index:
            return indicator_signal.wait

        days_before_date = stock.prices.index.get_loc(date)

        #no data for now
        if days_before_date <= self.long + self.signal + 1:
            return indicator_signal.wait

        #if data is not enough , returns wait
        if days_before_date < self.long or days_before_date < self.signal or days_before_date < self.short:
            return indicator_signal.wait

        assert date in stock.indicator_values[macd.dif]
        assert date in stock.indicator_values[macd.dea]

        current_dif = stock.indicator_values[macd.dif][date] 
        current_dea = stock.indicator_values[macd.dea][date]
        last_dif = stock.indicator_values[macd.dif][last_business_day(stock,date)]
        last_dea = stock.indicator_values[macd.dea][last_business_day(stock,date)]

        cross_type = cross.try_identify(last_dif,last_dea ,current_dif,current_dea)

        if cross_type == cross.golden and current_dif < 0 and current_dea < 0:
            return indicator_signal.buy
        elif cross_type == cross.dead and current_dif > 0 and current_dea > 0:
            return indicator_signal.sell
        else:
            return indicator_signal.wait
