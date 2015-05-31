from datetime import date
from data.stock import stock
from data.indicator import *
from data.sql import *
from analysis.combination_indicator import *

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
    name = Column(String(250), nullable=False, unique = True)
    
    total_money = Column(Float(4), nullable=False,default = 20000)
    first_investment_percent = Column(Float(2), nullable=False,default = 0.5)
    additional_investment_condition = Column(Float(2), nullable=False,default = 0.02)
    first_sell_percent = Column(Float(2), nullable=False,default = 0.5)
    additional_sell_condition = Column(Float(2), nullable=False,default = 0.02)
    holding_cycles = Column(Integer, nullable=False,default = 10000)
    loss_limit = Column(Float(2), nullable=False,default = 0.07)
    profit_limit = Column(Float(2), nullable=False,default = 100000)

    tolerant_days = Column(Integer, nullable=False,default = 5)
    indicator_combinator = Column(Integer,nullable = False,default = 1 )

    #evaluation    
    stocks_code = relationship(stock,secondary=stock_tracking,backref ='stocks_code', lazy='joined')
    start_evaluation = Column(Boolean, nullable=False)
    evaluation_start = Column(Date, nullable=False,default =  date(2005,6,6))
    evaluation_end = Column(Date, nullable=False,default =  date(2013,6,27))
    evaluation_parameters = relationship(indicator_parameter,backref = 'parameter', lazy='joined')
    evaluation_result = relationship(data.evaluation.evaluation_result, uselist=False, lazy='joined',cascade="save-update, merge, delete, delete-orphan")

    #learning
    start_learning = Column(Boolean, nullable=False)
    learning_done = Column(Boolean,nullable = False)
    learning_parameters = relationship(indicator_parameter,secondary=learning_progress,backref = backref('learning_parameters', lazy='joined'))
    
    #recommendation
    enable_recommendation = Column(Boolean, nullable=False)
    recommend_stocks = relationship(recommendation,
                                    collection_class = attribute_mapped_collection('stock_code'),
                                    cascade="all, delete-orphan")


    def __init__(self,name = 'analysis scheme'):

        #self.id = 123

        self.name = name
        '''Name'''

        self.learned = False
        '''whether it learned best parameters or not'''

        self.total_money = 20000

        self.first_investment_percent = 0.5

        self.additional_investment_condition = 0.02

        self.holding_cycles = 50

        self.loss_limit = 0.07

        self.profit_limit = 100000

        self.__indicators__ = []

        self.start_evaluation = False
        self.evaluation_start = date(2005,6,6)
        self.evaluation_end = date(2013,6,27)

        #default values
        self.stocks_code = [ stock('SHE:000559'),stock('SHA:601258'),stock('SHA:600876'),stock('SHA:600737'),stock('SHE:000039'),stock('SHE:002405'),stock('SHE:000997'),stock('SHE:002456'),stock('SHE:300168') ]

        self.start_learning = False
        self.learning_done = False

        self.enable_recommendation = False

        self.recommend_stocks = {}

    @reconstructor
    def init_on_load(self):    
        self.__indicators__ = []

    @property
    def indicators(self):
        if len(self.__indicators__) != len(self.evaluation_parameters):
            self.__indicators__.clear()
            for p in self.evaluation_parameters:
                #klass = getattr(getattr(__import__('analysis'),p.description.id.lower()),p.description.id.lower())
                klass = getattr(__import__('analysis'),p.description.id.lower())
                self.__indicators__.append(klass(p))
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

    def combine_indicators(self):
       if len(self.indicators) == 1:
           return self.indicators[0]
       elif self.indicator_combinator == combination_type.parallel:
           return parallel_indicator(self.indicators)
       elif self.indicator_combinator == combination_type.series:
           return series_indicator(self.indicators,self.tolerant_days)
       else: #default
           return parallel_indicator(self.indicators)
       #TODO add more combine

    def read_dict(self,dict):
        self.name = dict['Name']
        self.first_investment_percent = dict['FirstInvestmentPercent']
        self.additional_investment_condition = dict['AdditionalInvestmentCondition']
        self.holding_cycles = dict['HoldingCycles']
        self.loss_limit = dict['LossLimit']
        self.profit_limit = dict['ProfitLimit']
        self.tolerant_days = dict['TolerantDays']
        self.indicator_combinator = dict['CombinationType']

        self.start_evaluation = dict['StartEvaluation']
        import dateutil.parser
        self.evaluation_start = dateutil.parser.parse(dict['EvaluationStartTime']).date()
        self.evaluation_end = dateutil.parser.parse(dict['EvaluationEndTime']).date()
        indicator_parameters = {}
        for p in dict['EvaluationIndicators']:
            indicator_parameters[p['Name']] = p
        for p in self.evaluation_parameters:
            p.read_dict(indicator_parameters[p.description_id])

        self.stocks_code = [ stock(x['Code'],x['Name']) for x in dict['EvaluationStocks']]
            
        self.start_learning = dict['StartLearning']
        self.learning_done = dict['LearningDone']

        self.enable_recommendation = dict['EnableRecommendation']

    def to_dict(self):
        return {
                'ID':self.id,
                'Name':self.name,
                'FirstInvestmentPercent':self.first_investment_percent,
                'AdditionalInvestmentCondition':self.additional_investment_condition,
                'FirstSellPercent':self.first_sell_percent,
                'AdditionalSellCondition':self.additional_sell_condition,
                'HoldingCycles':self.holding_cycles,
                'LossLimit':self.loss_limit,
                'ProfitLimit':self.profit_limit,
                'TolerantDays':self.tolerant_days,
                'CombinationType':self.indicator_combinator,

                'StartEvaluation':self.start_evaluation,
                'EvaluationStartTime':self.evaluation_start.isoformat(),
                'EvaluationEndTime':self.evaluation_end.isoformat(),
                'EvaluationIndicators':[p.to_dict() for p in self.evaluation_parameters],
                'EvaluationStocks':[p.to_dict() for p in self.stocks_code],

                'StartLearning':self.start_learning,
                'LearningDone':self.learning_done,
                'LearningIndicators':[p.to_dict() for p in self.learning_parameters],

                'EnableRecommendation':self.enable_recommendation,
                }

    def __str__(self):
        return self.name


