from data.stock import stock
from analysis.indicator import *
from data.indicator import *
from datetime import *
from analysis.technical_analysis import *
from pandas.tseries.offsets import BDay
from pandas import Series

class kd(indicator_base):
    """KD indicator"""

    k_mark = 'k'
    d_mark = 'd'

    def __init__(self,parameter = None,description = None):                  
        if parameter == None:
            parameter = indicator_parameter(9,3,3)  
        if description == None:
            description = parameter.description

        if description != None:
            assert description.uppers[0] >= description.lowers[0]
            assert description.uppers[1] >= description.lowers[1]
            assert description.uppers[2] >= description.lowers[2]
        else:
            description = indicator_description('KD',3,'lambda p:p[0] in [9,19,34,55,89]')
            description.buy_point = u'出现金叉且K<=20且D<=20'
            description.sell_point = u'出现死叉'
            #n
            description.lowers[0] = 1
            description.uppers[0] = 100
            description.steps[0] = 1
            #m1
            description.lowers[1] = 1
            description.uppers[1] = 15
            description.steps[1] = 2
            #m2
            description.lowers[2] = 1
            description.uppers[2] = 15
            description.steps[2] = 2

        super(kd,self).__init__(parameter, description)
        
    @property
    def parameter(self):
        return self._parameter
    
    @parameter.setter
    def parameter(self,parameter):
        self._parameter = parameter
        if parameter != None:
            self.n =   clamp(parameter.params[0],self.description.lowers[0],self.description.uppers[0])
            self.m1 =  clamp(parameter.params[1],self.description.lowers[1],self.description.uppers[1])
            self.m2 =  clamp(parameter.params[2],self.description.lowers[2],self.description.uppers[2])

        
    def precompute(self,stock):
        assert stock.prices.index.size > 0,'{0}\'s prices is empty'.format(stock.code)

        values = rsv(stock,self.n)
        k = ewma(values,self.m1)
        d = ewma(k,self.m2)

        #cache values
        stock.indicator_values[kd.k_mark]=k
        stock.indicator_values[kd.d_mark]=d

    def get_signal(self,stock,date):
        '''BUY or SELL'''
        assert stock.prices.index.size != 0
        
        #no data for now
        if date < stock.prices.index[0] or date not in stock.prices.index:
            return indicator_signal.wait

        days_before_date = stock.prices.index.get_loc(date)

        #no data for now
        if days_before_date <= self.n + self.m1 + self.m2 + 1:
            return indicator_signal.wait

        assert date in stock.indicator_values[kd.k_mark]
        assert date in stock.indicator_values[kd.d_mark]

        current_k = stock.indicator_values[kd.k_mark][date] 
        current_d = stock.indicator_values[kd.d_mark][date]
        last_k = stock.indicator_values[kd.k_mark][last_business_day(stock,date)]
        last_d = stock.indicator_values[kd.d_mark][last_business_day(stock,date)]

        cross_type = cross.try_identify(last_k,last_d ,current_k,current_d)

        if cross_type == cross.golden or ( current_k <= 20 and current_d <= 20):
            return indicator_signal.buy
        #elif cross_type == cross.dead or ( current_k >= 80 and current_d >= 80):
        elif cross_type == cross.dead:
            return indicator_signal.sell
        else:
            return indicator_signal.wait
