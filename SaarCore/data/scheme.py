from data.stock import stock
from data.indicator import *
from data import Model
from sqlalchemy import Table , Column, ForeignKey, Integer, String, Boolean, Float, Date
from sqlalchemy.orm import relationship, backref, reconstructor

import data.evaluation
from data.learning import learning_progress
from data.recommendation import recommendation

stock_tracking = Table('stock_tracking',Model.metadata,
    Column('stock_code',String(10),ForeignKey('stock.code')),    
    Column('scheme_id',Integer,ForeignKey('scheme.id'))
)

class scheme(Model):
    """configuration of scheme"""
    __tablename__ = 'scheme'

    id = Column(Integer, primary_key=True,autoincrement = True)
    name = Column(String(250), nullable=False)

    first_investment_percent = Column(Float(2), nullable=False)
    additional_investment_condition = Column(Float(2), nullable=False)
    holding_cycles = Column(Integer, nullable=False)
    loss_limit = Column(Float(2), nullable=False)
    profit_limit = Column(Float(2), nullable=False)

    #evaluation    
    stocks_code = relationship(stock,secondary=stock_tracking,backref = backref('stocks_code',lazy = 'dynamic'))
    start_evaluation = Column(Boolean, nullable=False)
    evaluation_parameters = relationship(indicator_parameter,backref = 'parameter',lazy = 'select')
    evaluation_result = relationship(data.evaluation.evaluation_result, uselist=False)

    #learning
    start_learning = Column(Boolean, nullable=False)
    learning_done = Column(Boolean,nullable = False)
    learning_parameters = relationship(indicator_parameter,secondary=learning_progress,backref = backref('learning_parameters',lazy = 'dynamic'))
    
    #recommendation
    enable_recommendation = Column(Boolean, nullable=False)
    recommend_stocks = relationship(recommendation,backref ='learning_parameters',lazy = 'dynamic')


    def __init__(self,name = 'analysis scheme'):
        self.name = name
        '''Name'''

        self.learned = False
        '''whether it learned best parameters or not'''

        self.continual_learning = True

        self.total_money = 20000

        self.first_investment_percent = 0.5

        self.additional_investment_condition = 0.02

        self.holding_cycles = 50

        self.loss_limit = 0.07

        self.profit_limit = 100000

        self.__indicators__ = []

        self.start_evaluation = False
        #default values
        self.stocks_code = [ stock('SHE:000559'),stock('SHA:601258'),stock('SHA:600876'),stock('SHA:600737'),stock('SHE:000039'),stock('SHE:002405'),stock('SHE:000997'),stock('SHE:002456'),stock('SHE:300168') ]

        self.start_learning = False
        self.learning_done = False

        self.enable_recommendation = False

    @reconstructor
    def init_on_load(self):    
        self.__indicators__ = []
        indicator_module = __import__('analysis')
        for p in self.evaluation_parameters:
            klass = getattr(getattr(indicator_module,p.description.id),p.description.id)
            self.__indicators__.append(klass(p))

    @property
    def indicators(self):
        return self.__indicators__

    @indicators.setter
    def indicators(self,values):
        self.__indicators__ = values
        self.evaluation_parameters.clear()
        for i in values:
            self.evaluation_parameters.append(i.parameter)

    @property
    def stocks(self):
        return self.stocks_code

    @stocks.setter
    def stocks(self,stocks):
        self.stocks_code = stocks

    def append_indicators(self,indicator):
       self.indicators.append(indicator)

    def combine_indicators(self):
       if len(self.indicators) == 1:
           return self.indicators[0]
       else:#TODO
           return None

    def __str__(self):
        return self.name


