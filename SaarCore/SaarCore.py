from data.scheme import scheme
from data.stock import *
from data.indicator import indicator_parameter
from analysis import *
from datetime import datetime, timedelta
from pandas.tseries.offsets import *
from data import Model

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.scoping import scoped_session
from pandas import bdate_range, to_datetime

import os
engine = create_engine('sqlite:///../voystock.db')
Model.metadata.bind = engine
Model.metadata.create_all(engine)

DBSession = sessionmaker(bind = engine,expire_on_commit=False)
session = DBSession()

def merge_commit(result):
    session.merge(result)
    session.commit()

def analyse(scheme_id):
    '''
    Collect stock data and analyse them.(This always run after market is closed)
    This is core of recemmendation module.
    '''
    from analysis.recommendator import recommendator, today
    d = today()
    if datetime.now().hour <= 15:
        d = d - BDay(1)
    elif d.weekday() >= 5:
        d = d - BDay(1)

    sc = session.query(scheme).filter_by(id = scheme_id).first()
    if sc == None:
        print('scheme %s is not found.' % scheme_id)
        return

    last = datetime.combine(sc.last_run_date,datetime.min.time())
    if last >= d:
        return

    r = recommendator(sc)
    session.expunge(sc)
    for s in r.get_daliy_stocks(d):
        pass
    
    session.merge(sc)
    session.commit()
    print('recommendation done')

def analyse_mutiple_days(scheme_id,start,end):
    '''
    Collect stock data and analyse them.(This always run after market is closed)
    This is core of recemmendation module.
    '''
    from analysis.recommendator import recommendator

    sc = session.query(scheme).filter_by(id = scheme_id).first()
    if sc == None:
        print('scheme %s is not found.' % scheme_id)
        return

    r = recommendator(sc)
    for day in bdate_range(start,end):
        for s in r.get_daliy_stocks(day):
            pass
    session.commit()
    print('recommendation done')

def evaluate_scheme(scheme_id):
    sc = session.query(scheme).filter_by(id = scheme_id).first()
    if sc == None:
        print('scheme %s is not found.' % scheme_id)
        return

    from analysis.evaluation import evaluator,parallel_evaluator
    e = parallel_evaluator(sc)
    e.set_listener(merge_commit,merge_commit,merge_commit) 
    rate,money = e.calculate()

    session.commit()
    print('evaluation done')

def search_best_parameters(scheme_id):
    from analysis.learning_machine import learning_machine
    sc = session.query(scheme).filter_by(id = scheme_id).first()
    if sc == None:
        print('scheme %s is not found.' % scheme_id)
        return

    session.expunge(sc)
    e = learning_machine(sc)
    results = e.calculate_top_10_solutions()
    session.merge(sc)
    session.commit()
    print('learning done')
    

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
    sys.argv = ['','recommendation','1']
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
