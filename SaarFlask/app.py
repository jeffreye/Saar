"""
This script runs the application using a development server.
It contains the definition of routes and views for the application.
"""
from flask import Flask,request, Response
from auth import requires_auth
from datetime import date
from DateConverter import DateConverter
from flask.ext import FlaskAPI, status, exceptions

app = Flask(__name__)
app.url_map.converters['datetime'] = DateConverter

# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app

@app.route('/')
def hello():
    """Renders a sample page."""
    return 'Welcome to voystock'


@requires_auth
@app.route('/scheme/<int:scheme>',methods = ['POST', 'PUT' ])
def modify_scheme(scheme):
    '''Create a new scheme or update it'''
    pass

@requires_auth
@app.route('/scheme/<int:scheme>',methods = ['GET' ,'DELTE'])
def get_scheme(scheme):
    '''get a scheme values or delete it'''
    return str(scheme)



@requires_auth
@app.route('/evaluation/<int:scheme>',methods = ['GET','PUT','DELTE'])
def evaluate(scheme):

    if request.method == 'GET':
        '''get evaluation results'''
        pass
    elif request.method == 'PUT':
        '''start evaluation'''
        pass
    elif request.method == 'DELETE':
        '''stop evaluation'''
        pass
    else:
        raise exceptions.NotFound()

    return {'scheme':scheme}


@requires_auth
@app.route('/learning/<int:scheme>',methods =['GET','PUT','DELTE'])
def learn(scheme):
    '''start learning(run proc) or stop it'''

    if request.method == 'GET':
        '''get learning results'''
        pass
    elif request.method == 'PUT':
        '''start learning'''
        pass
    elif request.method == 'DELETE':
        '''stop learning'''
        pass
    else:
        raise exceptions.NotFound()

    return {'scheme':scheme}


@requires_auth
@app.route('/recommendation/<int:scheme>',methods = ['PUT','DELTE'])
def recommend(scheme):
    '''run proc'''
        
    if request.method == 'GET':
        '''get recommendation results'''
        pass
    elif request.method == 'PUT':
        '''start recommendation'''
        pass
    elif request.method == 'DELETE':
        '''stop recommendation'''
        pass
    else:
        raise exceptions.NotFound()

    return str(scheme)

@requires_auth
@app.route('/recommendation/<int:scheme>/<datetime:date>',methods = ['GET'])
def get_recommendation_on_date(scheme,date):
    return str([scheme,date])

if __name__ == '__main__':
    import os
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)
