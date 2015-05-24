import unittest
from datetime import datetime
from data.stock import *
from os.path import isfile
from os import remove


class Test_stock_test(unittest.TestCase):
    def __init__(self,*args, **kwargs):
        super(Test_stock_test, self).__init__(*args, **kwargs)

        self.__stocks__ = [ stock('SHE:000001'),
                            stock('SHE:000002'),
                            #stock('SHE:000333'),
                            #stock('SHE:000581'),
                            #stock('SHE:000725'),
                            #stock('SHE:000898'),
                            #stock('SHE:300070'),
                            #stock('SHA:600000'),
                            #stock('SHA:600008'),
                            stock('SHA:600068')
                            ]
        self.end_date = datetime(year = 2013,month = 6, day = 27)
        self.start_date =  datetime(year = 2005,month = 6,day = 6)
        
    
    def test_storing_csv(self):
        for s in self.__stocks__:
            csvfile = get_csv_path(s.code)
            if isfile(csvfile):
                remove(csvfile)
            s.pull_data(self.start_date,self.end_date)
            self.assertTrue(isfile(csvfile),s.code + '\'s data cannot be fetched.')
            remove(csvfile)

if __name__ == '__main__':
    unittest.main()
