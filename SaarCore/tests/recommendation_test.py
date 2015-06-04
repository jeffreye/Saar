import unittest
from data.scheme import scheme
from data.stock import stock
from data.indicator import *
from analysis.evaluation import evaluator,parallel_evaluator
from analysis.macd import macd
from analysis.kd import kd
from datetime import datetime
from analysis.recommendator import *

class Test_recommendation(unittest.TestCase):

    def __init__(self,*args, **kwargs):
        super(Test_recommendation, self).__init__(*args, **kwargs)
        test_scheme = scheme()        
        test_scheme.indicators = [ kd(indicator_parameter(9,1,15))]
        self.scheme = test_scheme
        self.__stocks__ = [ stock('SHE:000001'),
                            stock('SHE:000002'),
                            stock('SHE:000333'),
                            stock('SHE:000581'),
                            stock('SHE:000725'),
                            stock('SHE:000898'),
                            stock('SHE:300070'),
                            stock('SHA:600000'),
                            stock('SHA:600008'),
                            stock('SHA:600068')
                            ]
        self.test_stock = stock('SHA:600750')
        #self.test_stock.pull_data(datetime(2005,6,21) - timedelta(days = 100),datetime(2006,6,21))
            
    def test_recommendation(self):
        e = recommendator(self.scheme,log = True)
        buy = e.manipulate_stock(self.test_stock,datetime(2005,6,20))
        self.assertTrue(buy)

    def test_recommendation_sell(self):
        e = recommendator(self.scheme,log = True)

        buy = e.manipulate_stock(self.test_stock,datetime(2005,6,20))
        self.assertTrue(buy)
        self.scheme.recommend_stocks[self.test_stock.code].perform_operation()
        sell = e.manipulate_stock(self.test_stock,datetime(2005,6,21))

        self.assertTrue(sell)

    def test_recommendation_daliy(self):
        e = recommendator(self.scheme,debug_stocks = self.__stocks__ ,log = True)
        
        from pandas import bdate_range
        for day in bdate_range(start = today() - timedelta(days = 100),end = today() + timedelta(1)):
            for s in e.get_daliy_stocks(day):
                print('%s is a good choice at %s' % ( s,day))



        self.assertTrue(sell)
        

if __name__ == '__main__':
    unittest.main()
