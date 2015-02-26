#! python3
# -*- coding: utf-8 -*-

import os
import json
from flask import Flask
from flask import render_template, request

app = Flask(__name__)

def projectsdir():
    return os.path.join(os.path.dirname(__file__), 'projects')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/install.html')
def install():
    return render_template('install.html')

@app.route('/hello')
def hello_world():
    return "Hello World!!!"

@app.route('/project_list.html')
def projects():
    files = os.listdir(projectsdir())
    #data = json.dumps(files, ensure_ascii=False)
    #return data

    return render_template('projects.html', projects=files)

@app.route('/project/<projectname>', methods=['GET', 'POST'])
def project(projectname):
    print(projectname)
    if request.method == 'POST':
        #f = request.files['the_file']
        #f.save('/var/www/uploads/uploaded_file.txt')
        print(request.args)
        print(request.form)
        return 'failed'
    else:
        path = os.path.join(projectsdir(), projectname, 'current.json.txt')
        if not os.path.exists(path):
            return ('Not Found %s' % path, 404, [])
        return open(path, encoding='utf-8').read()

class PmpServer(object):
    def __init__(self, host='0.0.0.0', port=5000):
        self.host = host
        self.port = port #未使用

    def exec(self):
        app.debug = True
        app.run(host=self.host)
