"""
This script runs the application using a development server.
It contains the definition of routes and views for the application.
"""
from flask import Flask,request, Response
from auth import requires_auth
from datetime import date
from DateConverter import DateConverter

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
@app.route('/evaluation/<int:scheme>',methods = ['GET','DELTE'])
def evaluate(scheme):
    '''start evaluating or stop it'''
    pass

@requires_auth
@app.route('/evaluation/<int:scheme>/result',methods = ['GET'])
def get_evaluation_result(scheme):
    pass



@requires_auth
@app.route('/learning/<int:scheme>',methods =['GET','DELTE'])
def learn(scheme):
    '''start learning or stop it'''
    pass

@requires_auth
@app.route('/learning/<int:scheme>/result',methods = ['GET'])
def get_learning_result(scheme):
    pass



@requires_auth
@app.route('/recommendation/<int:scheme>',methods = ['GET','DELTE'])
def recommend(scheme):
    return str(scheme)

@requires_auth
@app.route('/recommendation/<int:scheme>/all',methods = ['GET'])
def get_recommendation(scheme):
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
