from data.stock import stock
import pandas
from enum import Enum
from datetime import timedelta
from pandas.tseries.offsets import BDay
import numpy as np

def last_business_day(stock,date):
    loc = stock.prices.index.get_loc(date)
    assert loc >= 0
    return stock.prices.index[loc - 1]
    

def clamp(my_value, min_value, max_value):
    assert max_value >= min_value
    result = max(min(my_value, max_value), min_value)
    assert max_value >= result >= min_value
    return result

def sma(data,n):
    n = int(n)
    return pandas.rolling_mean(data,window = n)

def rsv(stock,span):
    span = int(span)
    return (stock.prices.Close - pandas.rolling_min(stock.prices.Low,window = span))/(pandas.rolling_max(stock.prices.High,window = span) - pandas.rolling_min(stock.prices.Low,window = span)) * 100

def ewma(data,span):
    #return pandas.ewma(data,span = span,adjust = False)

    results = pandas.Series()
    span = int(span)

    criterion = data.map(lambda x: not np.isnan(x))
    data = data[criterion]

    #for i in range(min(span - 1,len(data))):
    #    results[data.index[i]] = np.NaN

    if len(data) < span:
        return results
    

    last_result = results[data.index[span]] = sum(data[:span]) / span

    if len(data) == span:
        return results

    alpha = 2 / (span + 1)
    beta = (span -1 )/(span + 1)
    for x in range(span,len(data)):
        last_result =  results[data.index[x]] = last_result * beta + data[x] *alpha

    return results

class cross(Enum):
    nothing = 0
    golden = 1
    dead = 2

    def try_identify(last_left,last_right,current_left,current_right):
        '''indentify the type of cross'''
        if current_left >= last_left and current_right >= last_right and last_left < last_right and current_left > current_right:
            return cross.golden
        elif current_left <= last_left and current_right <= last_right and last_left > last_right and current_left < current_right:
            return cross.dead
        else:
            return cross.nothing

    def try_identify_simple(last_left,last_right,current_left,current_right):
        '''indentify the type of cross'''
        if last_left < last_right and current_left > current_right:
            return cross.golden
        elif last_left > last_right and current_left < current_right:
            return cross.dead
        else:
            return cross.nothing



