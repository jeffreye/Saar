from itertools import product
from data.sql import *

class indicator_description(Model):
    """description of indicator"""
    __tablename__ ='description'    
    
    #id = Column(Integer, primary_key=True,autoincrement = True)
    id = Column(String(64), primary_key=True)
    #scheme_id = Column(Integer,ForeignKey('scheme.id'))
    #stock_code = Column(Integer,ForeignKey('stock.code'))
    parameter_count = Column(Integer,nullable = False , default = 0)
    constraint_function = Column(String(100))
    sell_point = Column(String(20),nullable = False,default = '')
    buy_point = Column(String(20),nullable = False,default = '')
    remark = Column(String(20),nullable = False,default = '')

    def __init__(self,klass,parameter_count,func_str = None):
        self.id = klass
        self.parameter_count = parameter_count

        #self.name = 'MACD'
        #'''indicator's name'''
        
        self.params = ['Parameter'] * 9

        self.uppers = [1000000] * 9

        self.lowers = [-1000000] * 9

        self.steps = [1] * 9

        self.constraint_function = func_str
        
        if self.constraint_function != None:
            self.pred = eval(self.constraint_function)
        else:
            self.pred = None


    @reconstructor
    def init_on_load(self):      
        self.params = ['Parameter'] * 9

        self.uppers = [1000000] * 9

        self.lowers = [-1000000] * 9

        self.steps = [1] * 9
        
        if self.constraint_function != None:
            self.pred = eval(self.constraint_function)
        else:
            self.pred = None

    def generate_all_parameters(self):
        
        parameter_list = []
        for i in range(self.parameter_count):
            parameter_list.append([x for x in range(self.lowers[i],self.uppers[i]+1,self.steps[i])])

        for p in product(*tuple(parameter_list)):
            if self.pred == None or self.pred(p):
                yield indicator_parameter(*p)

    def to_dict(self):
        return { 
                    'Name':self.id,
                    'SupportParameterCount':self.parameter_count,
                    'BuyPoint':self.buy_point,
                    'SellPoint':self.sell_point,
                    'Remark':self.remark
                }

class indicator_parameter(Model):
   """parameter of a indicator"""
   __tablename__ ='parameter'   
   
   id = Column(Integer, primary_key=True,autoincrement = True)
   description_id = Column(Integer,ForeignKey('description.id'))
   scheme_id = Column(Integer,ForeignKey('scheme.id'))
   stock_code = Column(Integer)

   description = relationship(indicator_description,uselist = False, lazy='joined')

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

   def to_dict(self):
       return {
                'Name':self.description_id,
                'Parameters':self.params
               }

   def from_dict(dict):
       result = indicator_parameter()
       result.description_id = dict['Name']
       result.params = dict['Parameters']
       return result