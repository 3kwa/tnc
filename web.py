import os.path

import cherrypy

from templates import serve_template

class App(object):

    @cherrypy.expose
    def index(self):
        return serve_template('index.html')


current_dir = os.path.dirname(os.path.abspath(__file__))
config_file = os.path.join(current_dir, 'web.conf')

cherrypy.quickstart(App(), config=config_file)
