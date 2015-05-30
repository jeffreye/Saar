import unittest

from data.scheme import scheme
from data.stock import stock
from data.indicator import *
from analysis.evaluation import evaluator,parallel_evaluator
from analysis.macd import macd

from data import Model

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite://')
Model.metadata.bind = engine
Model.metadata.create_all(engine)

DBSession = sessionmaker()
DBSession.bind = engine
session = DBSession()

class Test_sql_test(unittest.TestCase):
    
    # Scheme

    def test_add_scheme(self):
        s = scheme()
        s.indicators = [ macd(indicator_parameter(10,20,5))]
        s.stocks = [ stock('SHE:000001'),
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
        session.add(s)
        session.commit()
        added = session.query(scheme).filter(scheme.id == s.id).one()
        self.assertTrue(added != None)
        print(added.indicators)
        self.assertTrue(added.indicators[0] != None)
        return s

        
    def test_modify_scheme(self):
        s= self.test_add_scheme()
        s.profit_limit = 0.05
        session.commit()
        self.assertTrue(session.query(scheme).filter(scheme.id == s.id).one().profit_limit == 0.05)

    def test_delete_scheme(self):
        self.test_add_scheme()
        s = session.query(scheme).one()
        session.delete(s)
        session.commit()
        self.assertTrue(session.query(scheme).count() == 0)

    # Evaluation

    def test_evaluation(self):
        from data.evaluation import evaluation_result
        s = self.test_add_scheme()
        #start
        s.start_evaluation = True
        session.commit()

        #fake results
        s.evaluation_result = evaluation_result(scheme_id = s.id,progress = 1.0,done = True,money = 10000000,win_rate = 0.2)
        session.commit()

        #get
        self.assertTrue(session.query(scheme).filter(scheme.id == s.id).one().evaluation_result.done == True)

    def test_learning(self):

        s = self.test_add_scheme()
        #start
        s.start_learning = True
        session.commit()

        #fake results
        s.learning_parameters = [indicator_parameter(4,7,2),indicator_parameter(5,6,7)]
        s.learning_done = True
        session.commit()

        #get
        modified = session.query(scheme).filter(scheme.id == s.id).one()
        print(str(modified.learning_parameters))
        self.assertTrue(modified.learning_done == True)
        self.assertTrue(modified.learning_parameters[2].params[1] == 6)

    def test_recommendation(self):
        self.skipTest()
        return       
        from data.recommendation import recommendation
        from datetime import date

        s = self.test_add_scheme()
        #start
        s.enable_recommendation = True
        session.commit()

        #fake results
        s.recommend_stocks = [recommendation(scheme_id = s.id,date = date(2015,5,2),stock_code = "SHA:000001",operation = 1)]
        s.learning_done = True
        session.commit()

        #get
        modified = session.query(scheme).filter(scheme.id == s.id).one()
        print(modified.indicators)
        self.assertTrue(modified.learning_done == True)
        self.assertTrue(modified.indicators[0].parameter.params[0] == 4)

if __name__ == '__main__':
    unittest.main()
