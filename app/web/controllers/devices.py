import cherrypy

from app.config import Config
from app.models import Device, DeviceType, UserRole
from app.web.utils import authenticate, authorize


class Devices():
    def __init__(self):
        self.index_template = Config.jinja_env.get_template('devices/index.html')
        self.new_template = Config.jinja_env.get_template('devices/new.html')
        self.edit_template = Config.jinja_env.get_template('devices/edit.html')

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
    @cherrypy.tools.allow(methods=['GET'])
    @authenticate
    @authorize(UserRole.ADMIN)
    def edit(self, device_id: int):
        device = Device.find(device_id)
        return self.edit_template.render({'device': device})

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST'])
    @authenticate
    @authorize(UserRole.ADMIN)
    def create(self, name, description, kind, options):
        Device(name=name, description=description, type=kind, options=options).save()
        raise cherrypy.HTTPRedirect("/devices")

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST'])
    @authenticate
    @authorize(UserRole.ADMIN)
    def update(self, device_id, name, description, kind, options):
        device = Device.find(device_id)
        device.name = name
        device.description = description
        device.type = DeviceType.cast(kind)
        device.options = options
        device.save()
        raise cherrypy.HTTPRedirect("/devices")

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET'])
    @authenticate
    @authorize(UserRole.ADMIN)
    def destroy(self, device_id):
        Device.find(device_id).destroy()
        raise cherrypy.HTTPRedirect("/devices")
