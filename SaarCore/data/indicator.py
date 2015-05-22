from itertools import product

class indicator_parameter(object):
   """description of class"""
   
   def __init__(self,*args):
       self.indicator_id = 0

       self.scheme_id = 0

       self.stock_code = 0
       '''(0 stands for global parameter)'''


       if args != None:
           self.params = list(args) +  [0] * 9
       else:
           self.params = [0] * 9


class indicator_description(object):
    """description of class"""

    def __init__(self):
        self.id = 0

        self.name = 'MACD'
        '''indicator's name'''
        
        self.params = ['Parameter'] * 9

        self.uppers = [1000000] * 9

        self.lowers = [-1000000] * 9

        self.steps = [1] * 9

    def generate_all_parameters(self,parameter_numbers):
        
        parameter_list = []
        for i in range(parameter_numbers):
            parameter_list.append([x for x in range(self.lowers[i],self.uppers[i],self.steps[i])])

        for p in product(*tuple(parameter_list)):
            yield indicator_parameter(*p)


