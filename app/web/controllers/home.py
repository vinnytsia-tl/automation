import cherrypy

from app.web.utils import authenticate
from app.config import Config


class Home():
    def __init__(self):
        self.template = Config.jinja_env.get_template('home/index.html')

    @cherrypy.expose
    @authenticate
    def index(self):
        return self.template.render()
