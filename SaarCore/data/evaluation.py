from data.sql import *

class evaluation_result(Model):
    """description of class"""
    __tablename__ = 'evaluation_result'
        
    scheme_id = Column(Integer,ForeignKey('scheme.id'),primary_key = True)
    progress  = Column(Float(2),nullable = False,default = 0)
    #done = Column(Boolean,nullable = False)

    money = Column(Float(4),nullable = False,default = 0)
    money_used = Column(Float(4),nullable = False,default = 0)
    win_rate = Column(Float(2),nullable = False,default = 0)