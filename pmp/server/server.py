#! python3
# -*- coding: utf-8 -*-

import os
import json
import sqlite3
from contextlib import closing
from flask import Flask, g, request, session, render_template, \
     flash, redirect, url_for
from datetime import datetime


#configuration
DATABASE = 'pmp.db'
USERID   = 'admin'
PASSWORD = 'default'
SECRET_KEY = 'development key'


#create flask application
app = Flask(__name__)
app.config.from_object(__name__)

def init_db():
    """DB初期化。コマンドラインから呼び出す"""
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql') as f:
            db.cursor().executescript(f.read().decode('utf-8'))
        db.commit()

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def projectsdir():
    return os.path.join(os.path.dirname(__file__), 'projects')

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    g.db.close()


#handle http request
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['userid'] != app.config['USERID']:
            error = 'Invalid userid'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('index'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('index'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/install.html')
def install():
    return render_template('install.html')

@app.route('/apikey.html')
def show_apikey():
    if 'logged_in' in session and session['logged_in'] == True:
        return render_template('apikey.html')
    else:
        return render_template('login.html', error='APIキーを表示するにはログインしてください')

@app.route('/project_list.html')
def project_list():
    files = os.listdir(projectsdir())
    #data = json.dumps(files, ensure_ascii=False)
    #return data
    return render_template('projects.html', projects=files)

@app.route('/users.html')
def users():
    return render_template('users.html')

#handle http request(Web API)
@app.route('/pmp/api/projects/')
def api_project_list():
    return json.dumps(os.listdir(projectsdir()), ensure_ascii=False)

@app.route('/pmp/api/projects/<projectname>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def api_projects(projectname):
    def _get_project(projectname):
        path = os.path.join(projectsdir(), projectname, 'current.json.txt')
        if not os.path.exists(path):
            return ('Not Found %s' % path, 404, [])
        return open(path, encoding='utf-8').read()
    #-------
    print('projectname=[%s]' % projectname)
    if request.method == 'GET':
        return _get_project(projectname)
    elif request.method == 'POST':
        #f = request.files['the_file']
        #f.save('/var/www/uploads/uploaded_file.txt')
        #print(request.args)
        #print(request.form)
        print(request.remote_addr, request.remote_user)
        _now = datetime.now()
        path = os.path.join(projectsdir(), projectname, 'old',
            '%s_%s.txt' % (_now.strftime("%Y%m%d%H%M%S"), request.remote_addr))
        print(path)
        with open(path, "w", encoding='utf-8') as f:
            f.write(request.form['data'])
        return 'OK'
    else:
        path = os.path.join(projectsdir(), projectname, 'current.json.txt')
        if not os.path.exists(path):
            return ('Not Found %s' % path, 404, [])
        return open(path, encoding='utf-8').read()


#server class
class PmpServer(object):
    def __init__(self, host='0.0.0.0', port=5000):
        self.host = host
        self.port = port #未使用

    def exec(self):
        app.debug = True
        app.run(host=self.host)
