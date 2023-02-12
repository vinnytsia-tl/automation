import cherrypy
from jinja2 import Environment, PackageLoader

from .functions import authenticate


class Home():
    def __init__(self, database, session_max_time):
        self.database = database
        self.session_max_time = session_max_time
        self.template = Environment(loader=PackageLoader('app.web', '')).get_template('www/home/index.html')

    @cherrypy.expose
    @authenticate
    def index(self):
        return self.template.render()
