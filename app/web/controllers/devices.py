from typing import Optional

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
    def edit(self, device_id: str):
        device = Device.find(int(device_id))
        return self.edit_template.render({'device': device})

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST'])
    @authenticate
    @authorize(UserRole.ADMIN)
    def create(self, name: str, description: str, kind: str, options: str, disabled: Optional[str] = None):
        device_type = DeviceType.cast(kind)
        Device(name=name, description=description, type=device_type, options=options, disabled=disabled == '1').save()
        raise cherrypy.HTTPRedirect("/devices")

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST'])
    @authenticate
    @authorize(UserRole.ADMIN)
    def update(self, device_id: str, name: str, description: str, kind: str, options: str, disabled: Optional[str] = None):
        device = Device.find(int(device_id))
        device.name = name
        device.description = description
        device.type = DeviceType.cast(kind)
        device.options = options
        device.disabled = disabled == '1'
        device.save()
        raise cherrypy.HTTPRedirect("/devices")

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET'])
    @authenticate
    @authorize(UserRole.ADMIN)
    def destroy(self, device_id: str):
        Device.find(int(device_id)).destroy()
        raise cherrypy.HTTPRedirect("/devices")
