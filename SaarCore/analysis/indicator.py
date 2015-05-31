from enum import Enum, IntEnum
import math
from pandas.tseries.offsets import BDay

class indicator_base(object):
    """base class of all indicators"""

    def __init__(self,parameter,description):
        self.description = description
        parameter.description = description
        self.parameter = parameter

    def precompute(self,stock):
        pass

    def compute(self,stock,date):
        pass

    def get_signal(self,stock,date):
        '''BUY or SELL'''
        pass

    @property
    def parameter(self):
        return self._parameter

    @parameter.setter
    def parameter(self,value):
        self._parameter = value


    def __str__(self):
        return self.__class__.__name__ + str(tuple(self.parameter.params[:self.description.parameter_count]))

    
class indicator_signal(Enum):
    wait = (0)
    buy = (1)
    sell = (2)
    either = (3)

    def __init__(self, value):
        self._value_  = value

    @property
    def can_buy(self):
        return self.can(indicator_signal.buy)

    @property
    def can_sell(self):
        return self.can(indicator_signal.sell)

    def can(self,signal):
        return self._value_ & signal._value_ == signal._value_

    def __ior__(self,other):
        return indicator_signal(self._value_ | other._value_)

    def __or__(self,other):
        return indicator_signal(self._value_ | other._value_)