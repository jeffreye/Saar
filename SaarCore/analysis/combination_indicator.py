from data.stock import stock
from analysis.indicator import *
from data.indicator import *
from datetime import *
from analysis.technical_analysis import *
from pandas.tseries.offsets import BDay
from pandas import Series
from collections import deque
from enum import Enum

class combination_type(IntEnum):
    parallel = 1
    series = 2
    seperated = 3

class series_indicator(indicator_base):
    """buy and sell are based on a indicators list"""

    def __init__(self, indicators,tolerant_days = 5):
        self.indicators = indicators
        self.tolerant_days = tolerant_days
        self.last_results = {}
        self.day_past = 0
        for i in self.indicators:
            self.last_results[i] = deque([])
        
    def precompute(self,stock):
        for i in self.indicators:
            i.precompute(stock)

    def get_signal(self,stock,date):
        '''BUY or SELL'''
        if self.day_past > self.tolerant_days:
            for i in self.indicators:
                self.last_results[i].pop()
        
        # today
        for i in self.indicators:
            self.last_results[i].append(i.get_signal(stock,date))

        canBuy = self.satisfy(indicator_signal.buy)
        canSell = self.satisfy(indicator_signal.sell)

        if canBuy and canSell:
            return indicator_signal.either
        elif canBuy:
            return indicator_signal.buy
        elif canSell:
            return indicator_signal.sell
        else:
            return indicator_signal.wait

    def satisfy(self,signal):
        for r in self.last_results.values():
            result = indicator_signal.wait
            for s in r:
                result |= s
            if not s.can(signal):
                return False

        return True


class parallel_indicator(indicator_base):
    """buy and sell are based on a indicators list"""

    def __init__(self, indicators):
        self.indicators = indicators
        
    def precompute(self,stock):
        for i in self.indicators:
            i.precompute(stock)

    def get_signal(self,stock,date):
        '''BUY or SELL'''
        
        result = indicator_signal.wait
        for i in self.indicators:
            result |= i.get_signal(stock,date)

        return result



    

class separated_indicator(indicator_base):
    """buy and sell is based on different indicators list"""

    def __init__(self, buy_indicator,sell_indicator):
        self.buy_indicator = buy_indicator
        self.sell_indicator = sell_indicator
        super().__init__(indicator_parameter(),indicator_description('sep'))

    def precompute(self,stock):
        self.buy_indicator.precompute(stock)
        self.sell_indicator.precompute(stock)

    def get_signal(self,stock,date):
        '''BUY or SELL'''
        canBuy = self.buy_indicator.get_signal(stock,date).can_buy
        canSell = self.sell_indicator.get_signal(stock,date).can_sell

        if canBuy and canSell:
            return indicator_signal.either
        elif canBuy:
            return indicator_signal.buy
        elif canSell:
            return indicator_signal.sell
        else:
            return indicator_signal.wait
