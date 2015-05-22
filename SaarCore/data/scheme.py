from data.stock import stock

class scheme(object):
    """description of class"""

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

        self.indicators = []

        #default values
        self._stocks = [ stock('SHE:000559'),stock('SHA:601258'),stock('SHA:600876'),stock('SHA:600737'),stock('SHE:000039'),stock('SHE:002405'),stock('SHE:000997'),stock('SHE:002456'),stock('SHE:300168') ]

    
    def get_stocks(self):
        return self._stocks

    def set_stock(self,value):
        self._stocks = value

    stocks = property(get_stocks,set_stock)

    def append_indicators(self,indicator):
       self.indicators.append(indicator)

    def combine_indicators(self):
       if len(self.indicators) == 1:
           return self.indicators[0]
       else:#TODO
           return None

    def __str__(self):
        return self.name