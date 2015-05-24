from itertools import product
from data import Model
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, Float
from sqlalchemy.orm import relationship

class indicator_parameter(Model):
   """parameter of a indicator"""
   __tablename__ ='parameter'   
   
   id = Column(Integer, primary_key=True,autoincrement = True)
   descption_id = Column(Integer,ForeignKey('description.id'))
   scheme_id = Column(Integer,ForeignKey('scheme.id'))
   stock_code = Column(Integer,ForeignKey('stock.code'))

   def __init__(self,*args):
       self.indicator_id = 0

       self.scheme_id = 0

       self.stock_code = 0
       '''(0 stands for global parameter)'''


       if args != None:
           self.params = list(args) +  [0] * 9
       else:
           self.params = [0] * 9


class indicator_description(Model):
    """description of indicator"""
    __tablename__ ='description'    
    
    id = Column(Integer, primary_key=True,autoincrement = True)
    scheme_id = Column(Integer,ForeignKey('scheme.id'))
    stock_code = Column(Integer,ForeignKey('stock.code'))

    def __init__(self,pred = None):
        self.id = 0

        self.name = 'MACD'
        '''indicator's name'''
        
        self.params = ['Parameter'] * 9

        self.uppers = [1000000] * 9

        self.lowers = [-1000000] * 9

        self.steps = [1] * 9

        self.pred = pred

    def generate_all_parameters(self,parameter_numbers):
        
        parameter_list = []
        for i in range(parameter_numbers):
            parameter_list.append([x for x in range(self.lowers[i],self.uppers[i],self.steps[i])])

        for p in product(*tuple(parameter_list)):
            if self.pred == None or self.pred(p):
                yield indicator_parameter(*p)


