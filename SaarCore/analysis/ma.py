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
            
        if parameter == None:
            parameter = indicator_parameter(20)
        if description == None:
            description = parameter.description

        if description != None:
            assert description.uppers[0] >= description.lowers[0]
            assert description.uppers[1] >= description.lowers[1]
            assert description.uppers[2] >= description.lowers[2]
        else:
            description = indicator_description('MA',1)
            description.buy_point = u'MA(2*N)金叉MA(2*2N)'
            description.sell_point = u'MA(N)死叉MA(2*N)'
            #days
            description.lowers[0] = 1
            description.uppers[0] = 100
            description.steps[0] = 1

        super(ma,self).__init__(parameter, description)

    @property
    def parameter(self):
        return self._parameter
    
    @parameter.setter
    def parameter(self,parameter):
        self._parameter = parameter
        if parameter != None:
            self.days =   clamp(parameter.params[0],self.description.lowers[0],self.description.uppers[0])
            
        
    def precompute(self,stock):
        assert stock.prices.index.size > 0,'{0}\'s prices is empty'.format(stock.code)

        #cache values
        stock.indicator_values[ma1]=sma(stock.prices.Close,self.days)
        stock.indicator_values[ma2]=sma(stock.prices.Close,self.days*2)
        stock.indicator_values[ma4]=sma(stock.prices.Close,self.days*4)

    def get_signal(self,stock,date):
        '''BUY or SELL'''
        #if data is not enough , returns wait
        if stocks.prices.index.size == 0:
            raise BaseException('cannot retrieve stocks.prices')
        
        
        #no data for now
        if date < stock.prices.index[0] or date not in stock.prices.index:
            return indicator_signal.wait

        days_before_date = stock.prices.index.get_loc(date)

        #no data for now
        if days_before_date <= self.days *4 + 1:
            return indicator_signal.wait

        current_ma1 = stock.indicator_values[ma1][date] = sma(stock,date,self.days)
        current_ma2 = stock.indicator_values[ma2][date] = sma(stock,date,self.days*2)
        current_ma4 = stock.indicator_values[ma4][date] = sma(stock,date,self.days*4)
        
        buy_cross = cross.try_identify(stock.indicator_values[ma2][date - 1],stock.indicator_values[ma4][date - 1]
                                              ,current_ma2,current_ma4)
        sell_cross = cross.try_identify(stock.indicator_values[ma1][date - 1],stock.indicator_values[ma2][date - 1]
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