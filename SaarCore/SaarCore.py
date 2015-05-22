from analysis.learning_machine import learning_machine
from data.scheme import scheme
from analysis.macd import macd
from datetime import datetime
from pandas.tseries.offsets import BDay
from data import stock

def recollect_and_analyse_stocks():
    '''Collect stock data and analyse them.(This always run after market is closed)'''
    pass

def evaluate_scheme(scheme):
    pass

def search_best_parameters(scheme):
    pass

#def check_progress(): ##(write into database)
#    pass

if __name__ == '__main__':
        test_scheme = scheme()
        test_scheme.append_indicators(macd())
        test_scheme.stocks = [ stock('SHE:000001'),
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

        e = learning_machine(test_scheme,datetime(year = 2005,month = 6,day = 6),datetime(year = 2013,month = 6, day = 27))

        results = e.calculate_top_10_solutions()        
        for name,money in results.items():
            print(name + ' - ' + str(money))