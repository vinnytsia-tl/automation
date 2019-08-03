import cherrypy
from jinja2 import Environment, PackageLoader

from .functions import authorized


class Home():
    def __init__(self, database, session_max_time):
        self.database = database
        self.session_max_time = session_max_time
        self.template = Environment(loader=PackageLoader('app.web', '')).get_template('www/home/index.html')

    @cherrypy.expose
    def index(self):
        if not authorized(self.database, self.session_max_time):
            raise cherrypy.HTTPRedirect("/auth")
        title = "Automation VTL"
        return self.template.render(title=title)
