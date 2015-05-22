import unittest
from data.scheme import scheme
from data.stock import stock
from data.indicator import *
from analysis.evaluation import evaluator,parallel_evaluator
from analysis.learning_machine import learning_machine
from analysis.macd import macd
from datetime import datetime
from data.stock import stock,get_csv_path
from os.path import isfile
from os import remove

class Test_evaluator(unittest.TestCase):

    def __init__(self,*args, **kwargs):
        super(Test_evaluator, self).__init__(*args, **kwargs)
        test_scheme = scheme()
        
        test_scheme.append_indicators(macd(indicator_parameter(10,20,5)))
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
        self.end_date = datetime(year = 2013,month = 6, day = 27)
        self.start_date =  datetime(year = 2005,month = 6,day = 6)
        self.scheme.stocks = self.__stocks__
        
    
    def test_storing_csv(self):
        for s in self.__stocks__:
            csvfile = get_csv_path(s.code)
            if isfile(csvfile):
                remove(csvfile)
            s.pull_data(self.start_date,self.end_date)
            self.assertTrue(isfile(csvfile),s.code + '\'s data cannot be fetched.')
            remove(csvfile)
            
    def test_evaluator1(self):
        end_date = datetime(year = 2013,month = 6, day = 27)
        start_date =  datetime(year = 2005,month = 6,day = 6)
        e = evaluator(self.scheme,start_date,end_date)
        rate,money = e.calculate()
        self.assertTrue(0 <= rate <= 1)
        print('Win rate is {0} ,money = {1}'.format(rate,money))

    def test_evaluator2(self):
        end_date = datetime(year = 2013,month = 6, day = 27)
        start_date =  datetime(year = 2005,month = 6,day = 6)
        self.scheme.indicators = [macd(indicator_parameter(9,26,5))]
        e = evaluator(self.scheme,start_date,end_date)
        rate = e.calculate()
        self.assertTrue(0 <= rate <= 1)
        print('Win rate is {0} '.format(rate))
        
    def test_learning_machine(self):
        end_date = datetime(year = 2013,month = 6, day = 27)
        start_date =  datetime(year = 2005,month = 6,day = 6)
        e = learning_machine(self.scheme,start_date,end_date)

        results = e.calculate_top_10_solutions()        
        for name,rate in results.items():
            print(name + ' - ' + str(rate))
        
        
    def test_parallel_evaluator(self):
        end_date = datetime(year = 2013,month = 6, day = 27)
        start_date =  datetime(year = 2005,month = 6,day = 6)
        e = parallel_evaluator(self.scheme,start_date,end_date)
        print('Win rate is {0} '.format(e.calculate()))
        

if __name__ == '__main__':
    unittest.main()
