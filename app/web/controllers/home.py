import cherrypy

from app.config import Config


class Home():
    def __init__(self):
        self.template = Config.jinja_env.get_template('home/index.html')

    @cherrypy.expose
    @cherrypy.tools.authenticate()
    def index(self):
        return self.template.render()
