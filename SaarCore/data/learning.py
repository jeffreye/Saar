from data import Model
from sqlalchemy import Table , Column, ForeignKey, Integer, String, Boolean, Float, Date
from sqlalchemy.orm import relationship, backref

learning_progress = Table('learning_progress',Model.metadata,
    Column('parameter_id',Integer,ForeignKey('parameter.id')),    
    Column('scheme_id',Integer,ForeignKey('scheme.id'))
)