from data import Model
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, Float, Date

class recommendation(Model):
    """recommendation of scheme"""
    __tablename__ = 'recommendation'
    
    id = Column(Integer, primary_key=True,autoincrement = True)
    scheme_id = Column(Integer,ForeignKey('scheme.id'))
    date = Column(Date,index = True,nullable = False)
    stock_code = Column(String(10),ForeignKey('stock.code'),nullable = False)
    operation = Column(Integer,nullable = False)
