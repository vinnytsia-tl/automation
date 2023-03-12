import cherrypy

from app.config import Config
from app.web.utils import authenticate


class Home():
    def __init__(self):
        self.template = Config.jinja_env.get_template('home/index.html')

    @cherrypy.expose
    @authenticate
    def index(self):
        return self.template.render()
