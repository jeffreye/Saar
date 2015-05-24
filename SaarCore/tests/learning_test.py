import unittest
from analysis.learning_machine import learning_machine
from data.scheme import scheme
from data.stock import stock
from data.indicator import *
from analysis.macd import macd
from datetime import datetime

class Test_learning(unittest.TestCase):

    def __init__(self,*args, **kwargs):
        super(Test_learning, self).__init__(*args, **kwargs)
        test_scheme = scheme()
        
        test_scheme.append_indicators(macd(indicator_parameter(10,20,5)))
        self.scheme = test_scheme

        self.__stocks__ = [ stock('SHE:000001'),
                            #stock('SHE:000002'),
                            #stock('SHE:000333'),
                            #stock('SHE:000581'),
                            #stock('SHE:000725'),
                            #stock('SHE:000898'),
                            #stock('SHE:300070'),
                            #stock('SHA:600000'),
                            #stock('SHA:600008'),
                            #stock('SHA:600068')
                            ]
        self.scheme.stocks = self.__stocks__
                
        
    def test_learning_machine(self):
        end_date = datetime(year = 2015,month = 5, day = 23)
        start_date =  datetime(year = 2015,month = 5,day = 10)
        e = learning_machine(self.scheme,start_date,end_date)

        results = e.calculate_top_10_solutions()        
        for name,rate in results.items():
            print(name + ' - ' + str(rate))
        

if __name__ == '__main__':
    unittest.main()
