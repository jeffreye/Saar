import unittest
from data.scheme import scheme
from data.stock import stock
from data.indicator import *

class Test_scheme_test(unittest.TestCase):

    def __init__(self,*args, **kwargs):
        super(Test_scheme_test, self).__init__(*args, **kwargs)
        self.scheme = scheme()

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
            
    def test_scheme_stocks(self):
        self.scheme.stocks = self.__stocks__
        self.assertListEqual(self.scheme.stocks,self.__stocks__)

if __name__ == '__main__':
    unittest.main()
