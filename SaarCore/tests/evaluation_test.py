import unittest
from data.scheme import scheme
from data.stock import stock
from data.indicator import *
from analysis.evaluation import evaluator,parallel_evaluator
from analysis.macd import macd
from datetime import datetime

class Test_evaluator(unittest.TestCase):

    def __init__(self,*args, **kwargs):
        super(Test_evaluator, self).__init__(*args, **kwargs)
        test_scheme = scheme()
        
        test_scheme.indicators = [ macd(indicator_parameter(10,20,5))]
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
        test_scheme.evaluation_start = datetime(year = 2015,month = 5, day = 23)
        test_scheme.evaluation_end =  datetime(year = 2015,month = 4,day = 23)
        self.scheme.stocks = self.__stocks__
            
    def test_evaluator1(self):
        e = evaluator(self.scheme)
        rate,money = e.calculate()
        self.assertTrue(0 <= rate <= 1)
        print('Win rate is {0} ,money = {1}'.format(rate,money))

    def test_evaluator2(self):
        self.scheme.indicators = [macd(indicator_parameter(9,26,5))]
        e = evaluator(self.scheme)
        rate,money  = e.calculate()
        self.assertTrue(0 <= rate <= 1)
        print('Win rate is {0} '.format(rate))
        
    def test_parallel_evaluator(self):
        e = parallel_evaluator(self.scheme)
        rate,money  = e.calculate()
        print('Win rate is {0} '.format(rate))
        

if __name__ == '__main__':
    unittest.main()
