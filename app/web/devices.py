import cherrypy
from jinja2 import Environment, PackageLoader

from ..models import Device


class Devices():
    def __init__(self, database):
        self.database = database
        self.template = Environment(loader=PackageLoader('app.web', '')).get_template('www/devices/index.html')

    @cherrypy.expose
    def index(self):
        devices = Device.all(self.database)
        params = {'devices': devices}
        return self.template.render(params)
