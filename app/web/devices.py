import cherrypy
from jinja2 import Environment, PackageLoader

from ..models import Device
from .functions import authorize


class Devices():
    def __init__(self, database, session_max_time):
        self.database = database
        self.session_max_time = session_max_time
        self.index_template = Environment(loader=PackageLoader('app.web', '')).get_template('www/devices/index.html')
        self.new_template = Environment(loader=PackageLoader('app.web', '')).get_template('www/devices/new.html')

    @cherrypy.expose
    @authorize
    def index(self):
        devices = Device.all(self.database)
        params = {'devices': devices}
        return self.index_template.render(params)

    @cherrypy.expose
    @authorize
    def new(self):
        return self.new_template.render()

    @cherrypy.expose
    @authorize
    def post_new(self, name, description, type, options):
        Device.create2(self.database, name, description, type, options)
        raise cherrypy.HTTPRedirect("/devices")
