from data.scheme import scheme
from data.stock import *
from data.indicator import indicator_parameter
from analysis import *
from datetime import datetime, timedelta
from pandas.tseries.offsets import *
from data import Model

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import os
engine = create_engine('sqlite:///%s/../voystock.db' % os.getcwd())
Model.metadata.bind = engine
Model.metadata.create_all(engine)

DBSession = sessionmaker()
DBSession.bind = engine
session = DBSession()

def analyse(scheme_id):
    '''
    Collect stock data and analyse them.(This always run after market is closed)
    This is core of recemmendation module.
    '''
    from analysis.recommendator import recommendator, today
    if today().weekday() >= 5:
        print('today is not business day')
        return
    sc = session.query(scheme).filter_by(id == scheme_id).first()
    if sc == None:
        raise NameError('scheme %s is not found.' % scheme_id)
    r = recommendator(sc)
    for s in r.get_daliy_stocks():
        pass
    session.commit()

def evaluate_scheme(scheme_id):
    from analysis.evaluation import evaluator,parallel_evaluator
    sc = session.query(scheme).filter_by(id == scheme_id).first()
    if sc == None:
        raise NameError('scheme %s is not found.' % scheme_id)
    #session.expunge(sc)
    e = parallel_evaluator(sc)
    rate,money = e.calculate()
    #session.merge(sc)
    session.commit()

def search_best_parameters(scheme_id):
    from analysis.learning_machine import learning_machine
    sc = session.query(scheme).filter_by(id == scheme_id).first()
    if sc == None:
        raise NameError('scheme %s is not found.' % scheme_id)
    session.expunge(sc)
    e = learning_machine(sc)
    results = e.calculate_top_10_solutions()
    session.merge(sc)
    session.commit()
    

def test():
    test_scheme = scheme()
    test_scheme.loss_limit = 100
    test_scheme.indicators = [kd(indicator_parameter(9,1,15))]
    test_scheme.stocks = [
                        stock('SHA:600750'),
                        #stock('SHA:000012'),
                        #stock('SHA:600188'),
                        #stock('SHA:600219'),
                        #stock('SHA:600249'),
                        #stock('SHA:600718'),
                        #stock('SHA:600118'),
                        #stock('SHA:601928'),
                        #stock('SHA:603000'),
                        #stock('SHA:601688'),
                        #stock('SHA:603000'),
                        #stock('SHA:601988'),
                        #stock('SHA:600519'),
                        #stock('SHA:600795'),
                        #stock('SHE:000898'),
                        #stock('SHE:000792'),
                        #stock('SHE:000963'),
                        #stock('SHE:000401'),
                        #stock('SHE:000100'),
                        #stock('SHE:000536'),
                        ]
    test_scheme.evaluation_start = datetime(year = 2005,month = 6,day = 6)
    test_scheme.evaluation_end = datetime(year = 2012,month = 6, day = 27)
        
    #from analysis.learning_machine import learning_machine
    #e = learning_machine(test_scheme,log = True)
    #results = e.calculate_top_10_solutions()        
    #for name,money in results.items():
    #    print(name + ' - ' + str(money))
                        
    #e = evaluator(test_scheme,log = True)
    #rate,money = e.calculate()
    #print('Win rate is {0} ,money = {1}'.format(rate,money))



if __name__ == '__main__':
    print('working at ' + os.getcwd())
    import sys
    try:
        scheme_id = int(sys.argv[2])
        if sys.argv[1] =='recommendation':
            analyse(scheme_id)
        elif sys.argv[1] == 'learning':
            search_best_parameters(scheme_id)
        elif sys.argv[1] == 'evaluation':
            evaluate_scheme(scheme_id)
        else:
            test()
    except:
        print('fucking error %s' % sys.exc_info()[1])
    else:
        print('done ' + sys.argv[1])
