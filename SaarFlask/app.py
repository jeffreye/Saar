"""
This script runs the application using a development server.
It contains the definition of routes and views for the application.
"""
core_base_dir = 'SaarCore'
core_file = 'SaarCore.py'
py_proc = 'python %s %s %s'

from pathlib import Path
import os

proj_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_start_file(operation,scheme_id):
    return py_proc % (Path(proj_dir,core_base_dir,core_file),operation,scheme_id)

import sys
sys.path.append(str(Path(proj_dir,core_base_dir))+ os.sep)

from flask import Flask,request, Response
from auth import requires_auth
from DateConverter import DateConverter
from flask_sqlalchemy import SQLAlchemy
from data.scheme import scheme
from data.sql import *
from flask.ext.api import FlaskAPI, status, exceptions

app = FlaskAPI(__name__) # Browsable Web APIs for Flask
#app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../voystock.db'
app.url_map.converters['datetime'] = DateConverter

db = SQLAlchemy(app,session_options = { 'expire_on_commit':False })

#import actions
import SaarCore as actions

# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app

@requires_auth
@app.route('/init')
def init():
    """Renders a sample page."""
    try:
        Model.metadata.drop_all(db.engine)
        Model.metadata.create_all(db.engine)
        from analysis import kd
        s = scheme()
        s.indicators = [kd()]
        db.session.add(s)
        db.session.commit()
        return 'Welcome to voystock'
    except:
        import traceback
        return traceback.format_exc()
    finally:
        db.session.remove()
    
def open_file(filename):
    if sys.platform == "win32":
        os.startfile(filename)
    else:
        os.system('./%s&'%filename)

@requires_auth
@app.route('/update', methods=['GET'])
def shutdown():
    shutdown_server()
    try:
        os.chdir(proj_dir)
        open_file('reboot.sh')
        return 'Server rebooting...'
    except:
        import traceback
        return traceback.format_exc()

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        print('Not running with the Werkzeug Server')
    else:
        func()

@requires_auth
@app.route('/')
def hello():
    """Renders a sample page."""
    try:
        last_commit = os.popen("git rev-parse HEAD").read()
        return last_commit
    except:
        return 'Welcome to voystock'

@requires_auth
@app.route('/indicators')
def get_indicators():
    """Get all usable indicators"""
    # TODO: dynamically load all indicators
    return  [
                { 
                    'Name':'MACD',
                    'SupportParameterCount':3,
                    'BuyPoint':u'出现金叉',
                    'SellPoint':u'出现死叉',
                    'Remark':u'哦'
                 },
                { 
                    'Name':'KD',
                    'SupportParameterCount':3,
                    'BuyPoint':u'出现金叉且K<=20且D<=20',
                    'SellPoint':u'出现死叉',
                    'Remark':u'哦'
                 },
             ]


@requires_auth
@app.route('/scheme/',methods = ['POST','GET' ])
def modify_scheme():
    '''Create a new scheme or update it'''
    try:
        if request.method == 'GET':
            return 'hello'
        schemeData = request.data
        s = db.session.query(scheme).filter_by(id = schemeData['ID']).first() if 'ID' in schemeData else None
        if s == None:
            s = scheme()
            db.session.add(s)
        db.session.expunge(s)
        s.read_dict(schemeData)
        s = db.session.merge(s)
        db.session.commit()
        
        return str(s.id)
    except:
        import traceback
        return traceback.format_exc()
    finally:
        db.session.remove()

@requires_auth
@app.route('/scheme/<string:id>',methods = ['GET' ,'DELETE'])
def get_scheme(id):
    '''get a scheme values or delete it'''
    try:
        s = db.session.query(scheme).filter_by(id = id).first()
        if request.method == 'GET':
            if s == None:
                return 'null'
            else:
                return s.to_dict()
        elif request.method == 'DELETE':
            db.session.delete(s)
            db.session.commit()
            return 'null'
    except:
        import traceback
        return traceback.format_exc()
    finally:
        db.session.remove()

@requires_auth
@app.route('/scheme_all',methods = ['GET'])
def get_all_scheme():
    '''get a scheme values or delete it'''
    return [ s.to_dict() for s in db.session.query(scheme)]


def start_action(operation,scheme,start = None,end = None):
    #sql object cannot be used at other thread
    #db.session.expunge(scheme)

    #from multiprocessing import Process
    from threading import Thread
    if start == None and end == None:
        Thread(target = operation,args = (scheme.id,)).start()
    else:
        Thread(target = operation,args = (scheme.id,start,end)).start()

@requires_auth
@app.route('/evaluation/<string:id>',methods = ['GET','PUT','DELTE'])
def evaluate(id):
    try:    
        s = db.session.query(scheme).filter_by(id = id).first()    
        if s == None:
            return {
                'Progress':0,
                'AnnualizedReturn': 0,
                'WinRate':0
                }

        if request.method == 'GET':
            '''get evaluation results'''
            if s.evaluation_result == None:
                return {
                    'Progress':0,
                    'AnnualizedReturn': 0,
                    'WinRate':0
                    }
            else:
                principal = s.evaluation_result.money_used
                return {
                    'Progress':s.evaluation_result.progress,
                    'AnnualizedReturn': (s.evaluation_result.money - principal )/max(1,principal) / (( s.evaluation_end - s.evaluation_start ).days / 365),
                    'WinRate':s.evaluation_result.win_rate
                    }
        elif request.method == 'PUT':
            '''start evaluation and run proc'''    
            s.start_evaluation = True
            db.session.commit()        
            start_action(actions.evaluate_scheme,s)
        elif request.method == 'DELETE':
            '''stop evaluation'''
            s.start_evaluation = False
            db.session.commit()
        else:
            raise exceptions.NotFound()
        return {
            'Progress':0,
            'AnnualizedReturn': 0,
            'WinRate':0
            }
    except:
        import traceback
        return traceback.format_exc()
    finally:
        db.session.remove()


@requires_auth
@app.route('/learning/<string:id>',methods =['GET','PUT','DELTE'])
def learn(id):
    '''start learning(run proc) or stop it'''
    try:    
        s = db.session.query(scheme).filter_by(id = id).first()    
        if s == None:
            return { 'LearningDone' :False,
                     'BestParameters': None
                    }

        if request.method == 'GET':
            '''get learning results'''
            return { 'LearningDone' :s.learning_done,
                     'BestParameters': [ 
                                         {'Name':p.description.id ,'Parameters':p.params}
                                         for p in s.learning_parameters
                                        ]
                    }
        elif request.method == 'PUT':
            '''start learning and run proc'''
            s.start_learning = True
            db.session.commit()
            start_action(actions.search_best_parameters,s)
        elif request.method == 'DELETE':
            '''stop learning'''
            s.start_learning = False
            db.session.commit()
        else:
            raise exceptions.NotFound()
        return { 'LearningDone' :False,
                    'BestParameters': None
                }
    
    except:
        import traceback
        return traceback.format_exc()
    finally:
        db.session.remove()

@requires_auth
@app.route('/recommendation/<string:id>',methods = ['GET','PUT','DELTE'])
def recommend(id):
    '''Recommend stocks'''
    try:
        s = db.session.query(scheme).filter_by(id = id).first()    
        if s == None:
            return []
        
        if request.method == 'GET':
            '''get recommendation results'''
            return [ r.to_dict() for r in s.recommend_stocks ]
        elif request.method == 'PUT':
            '''start recommendation'''
            if len(request.data) == 2:
                
                import dateutil.parser
                start = dateutil.parser.parse(request.data['StartTime'])
                end = dateutil.parser.parse(request.data['EndTime'])

                s.enable_recommendation = True
                db.session.commit()
                start_action(actions.analyse,s,start,end)
            else:
                s.enable_recommendation = True
                db.session.commit()
                start_action(actions.analyse,s)
        elif request.method == 'DELETE':
            '''stop recommendation'''
            s.enable_recommendation = False
            db.session.commit()
        else:
            raise exceptions.NotFound()
        return []
    
    except:
        import traceback
        return traceback.format_exc()
    finally:
        db.session.remove()
    
@requires_auth
@app.route('/recommendation/<string:id>/<string:stock>',methods = ['GET'])
def perform_recommendation_operation(id,stock):
    """track a stock"""    
    try:
        s = db.session.query(scheme).filter_by(id = id).first()    
        if s == None:
            return 'null'
        state = s.recommend_stocks[stock].perform_operation()
        if state == stock_state.close_position:
            del s.recommend_stocks[stock]
        db.session.commit()
        
    except:
        import traceback
        return traceback.format_exc()
    finally:
        db.session.remove()

@requires_auth
@app.route('/recommendation/<string:id>/<datetime:date>',methods = ['GET'])
def get_recommendation_on_date(id,date):
    """get recommend stocks on specified date"""
    try:
        s = db.session.query(scheme).filter_by(id = id).first()    
        if s == None:
            return []
        return [ r.to_dict() for r in s.recommend_stocks if r.recommendation_operation_date == date ]
    except:
        import traceback
        return traceback.format_exc()
    finally:
        db.session.remove()


if __name__ == '__main__':
    #import os
    #HOST = os.environ.get('SERVER_HOST', '0.0.0.0')
    #try:
    #    PORT = int(os.environ.get('SERVER_PORT', '5555'))
    #except ValueError:
    #    PORT = 5555
    app.run('0.0.0.0', 5555)