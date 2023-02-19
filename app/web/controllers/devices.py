import cherrypy

from app.web.utils import authenticate, authorize
from app.models import Device, UserRole
from app.config import Config


class Devices():
    def __init__(self):
        self.index_template = Config.jinja_env.get_template('devices/index.html')
        self.new_template = Config.jinja_env.get_template('devices/new.html')

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET'])
    @authenticate
    @authorize
    def index(self, current_role: UserRole):
        devices = Device.all()
        params = {'devices': devices, 'isAdmin': current_role.value >= UserRole.ADMIN.value}
        return self.index_template.render(params)

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET'])
    @authenticate
    @authorize(UserRole.ADMIN)
    def new(self):
        return self.new_template.render()

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST'])
    @authenticate
    @authorize(UserRole.ADMIN)
    def create(self, name, description, kind, options):
        Device(name=name, description=description, type=kind, options=options).save()
        raise cherrypy.HTTPRedirect("/devices")
