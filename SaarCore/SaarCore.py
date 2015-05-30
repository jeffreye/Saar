from analysis.learning_machine import learning_machine
from data.scheme import scheme
from analysis import *
from datetime import datetime
from pandas.tseries.offsets import BDay
from data.stock import stock
from data.indicator import indicator_parameter
from analysis.evaluation import evaluator,parallel_evaluator
from data import Model
from data.evaluation import evaluation_result

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///../voystock.db')
Model.metadata.bind = engine
Model.metadata.create_all(engine)

DBSession = sessionmaker()
DBSession.bind = engine
session = DBSession()

def recollect_and_analyse_stocks():
    '''
    Collect stock data and analyse them.(This always run after market is closed)
    This is core of recemmendation module.
    '''
    for sc in session.query(scheme).all():
        pass

def evaluate_scheme(scheme_id):
    sc = session.query(scheme).filter(scheme.id == scheme_id).first()
    if sc == None:
        return
    e = parallel_evaluator(test_scheme)
    rate,money = e.calculate()

    sc.evaluation_result = evaluation_result(scheme_id = scheme_id,progress = 1, money = money,win_rate = rate)
    session.commit()

def search_best_parameters(scheme_id):
    sc = session.query(scheme).filter(scheme.id == scheme_id).first()
    if sc == None:
        return
    #e = learning_machine(test_scheme,datetime(year = 2005,month = 6,day = 6),datetime(year = 2013,month = 6, day = 27),log = True)
    #results = e.calculate_top_10_solutions()  


def recommend_stocks():
    pass

if __name__ == '__main__':
    def learn_kd():
        test_scheme = scheme()
        test_scheme.indicators = [kd(indicator_parameter(9,3,3))]
        test_scheme.stocks = [

                            stock('SHA:600150'),
                            ]

        #e = learning_machine(test_scheme,datetime(year = 2005,month = 6,day = 6),datetime(year = 2013,month = 6, day = 27),log = True)
        #results = e.calculate_top_10_solutions()        
        #for name,money in results.items():
        #    print(name + ' - ' + str(money))
        
        e = parallel_evaluator(test_scheme,datetime(year = 2005,month = 6,day = 6),datetime(year = 2013,month = 6, day = 27),log = True)
        rate,money = e.calculate()
        print('Win rate is {0} ,money = {1}'.format(rate,money))


    learn_kd()
