from data.sql import *

learning_progress = Table('learning_progress',Model.metadata,
    Column('parameter_id',Integer,ForeignKey('parameter.id')),    
    Column('scheme_id',Integer,ForeignKey('scheme.id'))
)