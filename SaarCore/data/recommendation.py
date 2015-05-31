from data.sql import *
from data.stock import stock_state
from enum import IntEnum
from datetime import *
from pandas.tseries.offsets import *
    
class recommendation_operation(IntEnum):
    wait = 0
    buy = 1
    sell = 2

def today():
    return Day(normalize=True).rollforward(datetime.now()-timedelta(1))

class recommendation(Model):
    """recommendation of scheme"""
    __tablename__ = 'recommendation'
    
    id = Column(Integer, primary_key=True,autoincrement = True)
    scheme_id = Column(Integer,ForeignKey('scheme.id'))
    buy_date = Column(Date,nullable = False)
    last_operation_date = Column(Date,nullable = False)
    recommendation_operation_date = Column(Date,nullable = False)
    stock_code = Column(String(10),index = True,nullable = False)
    stock_name = Column(String(20))
    operation = Column(Integer,nullable = False) #recommendation_operation
    state = Column(Integer,nullable = False,default = 0) #stock_state

    perform = {
                    stock_state.close_position: {
                                                    recommendation_operation.wait:stock_state.close_position,
                                                    recommendation_operation.buy:stock_state.hold_position,
                                                },
                    stock_state.hold_position: {
                                                    recommendation_operation.wait:stock_state.hold_position,
                                                    recommendation_operation.buy:stock_state.open_position,
                                                    recommendation_operation.sell:stock_state.close_position,
                                                },
                    stock_state.open_position: {
                                                    recommendation_operation.wait:stock_state.open_position,
                                                    recommendation_operation.sell:stock_state.hold_position,
                                                },
                }

    def perform_operation(self):
        self.state = recommendation.perform[self.state][self.operation]
        self.operation = recommendation_operation.wait
        self.last_operation_date = today()
        return self.state

    def to_dict(self):
        return {
                    'Code':self.stock_code,
                    'Name':self.stock_name,
                    'Operation':self.operation,
                    'BuyDate':self.date,
                    'State':self.state,
                }

    def __repr__(self):
        return '<stock=%s  buy_date=%s state=%s last_operation=%s >' % (self.stock_code,self.buy_date,self.state,self.last_operation_date)
