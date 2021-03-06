from app import db
from data.scheme import scheme

def merge_commit(result):
    db.session.merge(result)
    db.session.commit()

def analyse(scheme_id):
    '''
    Collect stock data and analyse them.(This always run after market is closed)
    This is core of recemmendation module.
    '''
    from analysis.recommendator import recommendator, today
    if today().weekday() >= 5:
        print('today is not business day')
        return
    
    sc = db.session.query(scheme).filter_by(id = scheme_id).first()
    if sc == None:
        raise NameError('scheme %s is not found.' % scheme_id)

    r = recommendator(sc)
    for s in r.get_daliy_stocks():
        pass

    db.session.commit()
    print('recommendation done')
    
def analyse_mutiple_days(scheme_id,start,end):
    '''
    Collect stock data and analyse them.(This always run after market is closed)
    This is core of recemmendation module.
    '''
    from analysis.recommendator import recommendator

    sc = session.query(scheme).filter_by(id = scheme_id).first()
    if sc == None:
        raise NameError('scheme %s is not found.' % scheme_id)

    r = recommendator(sc)
    for day in bdate_range(start,end):
        for s in r.get_daliy_stocks(day):
            pass
    session.commit()
    print('recommendation done')

def evaluate_scheme(scheme_id):
    sc = db.session.query(scheme).filter_by(id = scheme_id).first()
    if sc == None:
        raise NameError('scheme %s is not found.' % scheme_id)

    from analysis.evaluation import evaluator,parallel_evaluator
    e = parallel_evaluator(sc)
    e.set_listener(merge_commit,merge_commit,merge_commit) 
    rate,money = e.calculate()

    db.session.commit()
    print('evaluation done')

def search_best_parameters(scheme_id):
    sc = db.session.query(scheme).filter_by(id = scheme_id).first()
    if sc == None:
        raise NameError('scheme %s is not found.' % scheme_id)

    from analysis.learning_machine import learning_machine
    session.expunge(sc)
    e = learning_machine(sc)
    results = e.calculate_top_10_solutions()
    db.session.merge(sc)
    db.session.commit()
    print('learning done')