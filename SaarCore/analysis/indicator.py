from enum import Enum
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
    def parameter_count(self):
        return 0

    @property
    def parameter(self):
        return self._parameter

    @parameter.setter
    def parameter(self,value):
        self._parameter = value


    def __str__(self):
        return self.__class__.__name__ + str(tuple(self.parameter.params[:self.parameter_count]))

    
class indicator_signal(Enum):
    """description of class"""
    wait = 0
    buy = 1
    sell = 2

