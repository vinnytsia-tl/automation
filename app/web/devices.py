import cherrypy
from jinja2 import Environment, PackageLoader

from ..models import Device


class Devices():
    def __init__(self, database):
        self.database = database
        self.index_template = Environment(loader=PackageLoader('app.web', '')).get_template('www/devices/index.html')
        self.new_template = Environment(loader=PackageLoader('app.web', '')).get_template('www/devices/new.html')

    @cherrypy.expose
    def index(self):
        devices = Device.all(self.database)
        params = {'devices': devices}
        return self.index_template.render(params)

    @cherrypy.expose
    def new(self):
        return self.new_template.render()

    @cherrypy.expose
    def post_new(self, name, description, type, options):
        Device.create2(self.database, name, description, type, options)
        raise cherrypy.HTTPRedirect("/devices")
