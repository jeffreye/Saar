from app import db

def analyse(sc):
    '''
    Collect stock data and analyse them.(This always run after market is closed)
    This is core of recemmendation module.
    '''
    if sc == None:
        raise NameError('scheme %s is not found.' % scheme_id)
    from analysis.recommendator import recommendator, today
    if today().weekday() >= 5:
        print('today is not business day')
        return
    r = recommendator(sc)
    for s in r.get_daliy_stocks():
        pass

    db.session.merge(sc)
    db.session.commit()
    print('recommendation done')

def evaluate_scheme(sc):
    if sc == None:
        raise NameError('scheme %s is not found.' % scheme_id)
    from analysis.evaluation import evaluator,parallel_evaluator
    e = parallel_evaluator(sc)
    rate,money = e.calculate()

    db.session.merge(sc)
    db.session.commit()
    print('evaluation done')

def search_best_parameters(sc):
    if sc == None:
        raise NameError('scheme %s is not found.' % scheme_id)
    from analysis.learning_machine import learning_machine
    e = learning_machine(sc)
    results = e.calculate_top_10_solutions()
    db.session.merge(sc)
    db.session.commit()
    print('learning done')