import os
import cherrypy
import pandas as pd


class KKT(object):
    @cherrypy.expose
    def index(self):
        return 'index'

    @cherrypy.expose
    def dictionary(self):
        return open('kkt.html', 'r')


@cherrypy.expose
@cherrypy.tools.json_out()
class DictGenerator(object):
    @cherrypy.tools.accept(media='application/json')
    def GET(self):
        data = pd.read_html('Dictionary.html')[0]
        data.columns = ['key', 'description', 'default', 'type', 'aggr', 'doc']
        data['id'] = list(range(len(data)))
        data['aggr'] = data['aggr'].apply(
            lambda x: True if x == 'Возможно' else False)
        return data.to_dict(orient='records')


if __name__ == '__main__':
    conf = {
        '/': {
            'tools.staticdir.root': os.path.abspath(os.getcwd())
        },
        '/generator': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Content-Type', 'application/json')]
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './public'
        }
    }
    app = KKT()
    app.generator = DictGenerator()
    cherrypy.config.update({'server.socket_host': '0.0.0.0'})
    cherrypy.config.update({'server.socket_port': 8080})
    cherrypy.quickstart(app, '/', conf)
