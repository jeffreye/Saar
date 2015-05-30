from data.sql import *

class evaluation_result(Model):
    """description of class"""
    __tablename__ = 'evaluation_result'
        
    scheme_id = Column(Integer,ForeignKey('scheme.id'),primary_key = True)
    progress  = Column(Float(2),nullable = False)
    #done = Column(Boolean,nullable = False)

    money = Column(Float(4),nullable = False)
    win_rate = Column(Float(2),nullable = False)