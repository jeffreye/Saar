from itertools import product
from data import Model
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, Float, Table
from sqlalchemy.orm import relationship,reconstructor

class indicator_description(Model):
    """description of indicator"""
    __tablename__ ='description'    
    
    #id = Column(Integer, primary_key=True,autoincrement = True)
    id = Column(String(64), primary_key=True)
    #scheme_id = Column(Integer,ForeignKey('scheme.id'))
    #stock_code = Column(Integer,ForeignKey('stock.code'))

    def __init__(self,klass = 'macd',pred = None):
        self.id = klass

        #self.name = 'MACD'
        #'''indicator's name'''
        
        self.params = ['Parameter'] * 9

        self.uppers = [1000000] * 9

        self.lowers = [-1000000] * 9

        self.steps = [1] * 9

        self.pred = pred


    @reconstructor
    def init_on_load(self):      
        self.params = ['Parameter'] * 9

        self.uppers = [1000000] * 9

        self.lowers = [-1000000] * 9

        self.steps = [1] * 9

        self.pred = None

    def generate_all_parameters(self,parameter_numbers):
        
        parameter_list = []
        for i in range(parameter_numbers):
            parameter_list.append([x for x in range(self.lowers[i],self.uppers[i],self.steps[i])])

        for p in product(*tuple(parameter_list)):
            if self.pred == None or self.pred(p):
                yield indicator_parameter(*p)

class indicator_parameter(Model):
   """parameter of a indicator"""
   __tablename__ ='parameter'   
   
   id = Column(Integer, primary_key=True,autoincrement = True)
   descption_id = Column(Integer,ForeignKey('description.id'))
   scheme_id = Column(Integer,ForeignKey('scheme.id'))
   stock_code = Column(Integer,ForeignKey('stock.code'))

   description = relationship(indicator_description,uselist = False)

   param0 = Column(Float(2))
   param1 = Column(Float(2))
   param2 = Column(Float(2))
   param3 = Column(Float(2))
   param4 = Column(Float(2))
   param5 = Column(Float(2))
   param6 = Column(Float(2))
   param7 = Column(Float(2))
   param8 = Column(Float(2))

   def __init__(self,*args):
       self.indicator_id = 0

       self.scheme_id = 0

       self.stock_code = 0
       '''(0 stands for global parameter)'''


       if args != None:
           self.params = list(args) +  [0] * 9
       else:
           self.params = [0] * 9
           
           
   @reconstructor
   def init_on_load(self):      
        self.__params__ = [0] * 9
        for i in range(9):
            self.__params__[i] = getattr(self,'param' + str(i))


   @property
   def params(self):
       return self.__params__

   @params.setter
   def params(self,values):
       self.__params__ = values
       for i in range(len(values)):
           setattr(self,'param' + str(i),values[i])
       for i in range(len(values),9):
           setattr(self,'param' + str(i),0)
       return self.__params__

