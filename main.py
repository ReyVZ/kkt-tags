import os
import cherrypy
import sqlite3
import pandas as pd
import requests
from jinja2 import Environment, PackageLoader, select_autoescape


from cherrypy.lib import auth_basic

USERS = {'admin': '123'}
DB = 'data.db'
ENV = Environment(loader=PackageLoader('main', 'templates'),
                  autoescape=select_autoescape(['html']))


def start_database():
    with sqlite3.connect(DB) as con:
        sql = '''create table if not exists user (
            id integer primary key asc autoincrement, 
            username text not null unique, 
            password text not null
            )'''
        con.execute(sql)


def stop_database():
    pass


def validate_password(realm, username, password):
    with sqlite3.connect(DB) as con:
        sql = 'select username, password from user'
        users = dict(con.execute(sql).fetchall())
        if username in users and users[username] == password:
            return True
        return False


class KKT(object):
    @cherrypy.expose
    def index(self):
        if 'username' in cherrypy.session:
            res = ENV.get_template('index.html')
            return res.render(username=cherrypy.session['username'])
        else:
            raise cherrypy.HTTPRedirect('/login')

    @cherrypy.expose
    def kkt(self):
        if 'username' in cherrypy.session:
            res = ENV.get_template('kkt.html')
            return res.render(active1='active', username=cherrypy.session['username'])
        else:
            raise cherrypy.HTTPRedirect('/login')

    @cherrypy.expose
    def kkt_instruction(self):
        if 'username' in cherrypy.session:
            res = ENV.get_template('kkt_instruction.html')
            return res.render(active2='active', username=cherrypy.session['username'])
        else:
            raise cherrypy.HTTPRedirect('/login')

    @cherrypy.expose
    def login(self):
        if 'username' in cherrypy.session:
            raise cherrypy.HTTPRedirect('/index')
        else:
            error = ''
            res = ENV.get_template('login.html')
            return res.render(error=error)

    @cherrypy.expose
    def auth(self, username='', password=''):
        if validate_password('localhost', username, password):
            cherrypy.session['username'] = username
            raise cherrypy.HTTPRedirect('/index')
        else:
            error = 'Имя пользователя или пароль неверны'
            res = ENV.get_template('login.html')
            return res.render(error=error)

    @cherrypy.expose
    def logout(self):
        if 'username' in cherrypy.session:
            cherrypy.session.pop('username', None)
        raise cherrypy.HTTPRedirect('/login')

    @cherrypy.expose
    def dictionary(self):
        return open('old_kkt.html', 'r')


@cherrypy.expose
@cherrypy.tools.json_out()
class DictGenerator(object):
    @cherrypy.tools.accept(media='application/json')
    def GET(self):
        data = None
        try:
            r = requests.get('https://webreport.taxcom.ru/Info/Dictionary')
            if r.status_code == 200:
                with open('dict_backup.html', 'w') as f:
                    f.write(r.text)
                data = pd.read_html(r.text)[0]
        except:
            cherrypy.log('NOT FOUND NEW DICTIONARY')
        if data is None:
            data = pd.read_html(open('dict_backup.html', 'r').read())[0]

        data.columns = ['key', 'description', 'default', 'type', 'aggr', 'doc']
        data['id'] = list(range(len(data)))
        data['aggr'] = data['aggr'].apply(
            lambda x: True if x == 'Возможно' else False)
        cherrypy.response.headers['Access-Control-Allow-Origin'] = '*'
        return data.to_dict(orient='records')


if __name__ == '__main__':
    conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd()),
            'log.error_file': 'logs/web.log',
            'log.access_file': 'logs/access.log'
        },
        '/generator': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Content-Type', 'application/json')]
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './public'
        },
        '/favicon.ico': {
            'tools.staticfile.on': True,
            'tools.staticfile.filename': os.path.join(os.path.abspath(os.getcwd()),
                                                      'public', 'img', 'favicon.ico')
        },
        '/protected/area': {
            'tools.auth_basic.on': True,
            'tools.auth_basic.realm': 'localhost',
            'tools.auth_basic.checkpassword': validate_password,
            'tools.auth_basic.accept_charset': 'UTF-8',
        }
    }
    cherrypy.engine.subscribe('start', start_database)
    cherrypy.engine.subscribe('stop', stop_database)
    app = KKT()
    app.generator = DictGenerator()
    cherrypy.config.update({'server.socket_host': '0.0.0.0'})
    # cherrypy.config.update({'server.socket_host': '127.0.0.1'})
    cherrypy.config.update({'server.socket_port': 8080})
    cherrypy.quickstart(app, '/', conf)
