import cherrypy
from jinja2 import Environment, PackageLoader

from ..models import Rule
from .functions import authorize


class Rules():
    def __init__(self, database, session_max_time):
        self.database = database
        self.session_max_time = session_max_time
        self.index_template = Environment(loader=PackageLoader('app.web', '')).get_template('www/rules/index.html')
        self.new_template = Environment(loader=PackageLoader('app.web', '')).get_template('www/rules/new.html')

    @cherrypy.expose
    @authorize
    def index(self):
        rules = Rule.all(self.database)
        params = {'rules': rules}
        return self.index_template.render(params)

    @cherrypy.expose
    @authorize
    def new(self):
        return self.new_template.render()

    @cherrypy.expose
    @authorize
    def post_new(self, name, description, device_id, start_time, duration):
        Rule.create2(self.database, name, description, device_id, start_time, duration)
        raise cherrypy.HTTPRedirect("/rules")
