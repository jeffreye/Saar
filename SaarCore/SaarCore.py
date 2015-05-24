from analysis.learning_machine import learning_machine
from data.scheme import scheme
from analysis.macd import macd
from datetime import datetime
from pandas.tseries.offsets import BDay
from data.stock import stock
from data.indicator import indicator_parameter
from analysis.evaluation import evaluator,parallel_evaluator
from data import Model

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///../voystock.db')
Model.metadata.bind = engine
Model.metadata.create_all(engine)

DBSession = sessionmaker()
DBSession.bind = engine
session = DBSession()

def recollect_and_analyse_stocks():
    '''Collect stock data and analyse them.(This always run after market is closed)'''
    pass

def evaluate_scheme(scheme_id):
    sc = session.filter(scheme.id == scheme_id).first()

    pass

def search_best_parameters(scheme_id):
    pass

def recommend_stocks():
    pass

if __name__ == '__main__':
    def test():
        test_scheme = scheme()
        test_scheme.indicators = [ macd(indicator_parameter(4,7,2))]
        test_scheme.stocks = [
                            stock('SHE:000001'),
                            stock('SHE:000002'),
                            stock('SHE:000333'),
                            stock('SHE:000581'),
                            stock('SHE:000725'),
                            stock('SHE:000898'),
                            stock('SHE:300070'),
                            stock('SHA:600000'),
                            stock('SHA:600008'),
                            stock('SHA:600068'),
                            stock('SHA:600150')
                            ]

        e = learning_machine(test_scheme,datetime(year = 2005,month = 6,day = 6),datetime(year = 2013,month = 6, day = 27),log = True)
        results = e.calculate_top_10_solutions()        
        for name,money in results.items():
            print(name + ' - ' + str(money))
        
        #e = parallel_evaluator(test_scheme,datetime(year = 2005,month = 6,day = 6),datetime(year = 2013,month = 6, day = 27),log = True)
        #rate,money = e.calculate()
        #print('Win rate is {0} ,money = {1}'.format(rate,money))
    test()
