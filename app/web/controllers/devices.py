from typing import Optional

import cherrypy

from app.config import Config
from app.models import Device, DeviceType, UserRole


class Devices():
    def __init__(self):
        self.index_template = Config.jinja_env.get_template('devices/index.html')
        self.new_template = Config.jinja_env.get_template('devices/new.html')
        self.edit_template = Config.jinja_env.get_template('devices/edit.html')

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET'])
    @cherrypy.tools.authenticate()
    @cherrypy.tools.authorize()
    def index(self):
        current_role = UserRole(cherrypy.session['current_role'])
        devices = Device.all()
        params = {'devices': devices, 'isAdmin': current_role.value >= UserRole.ADMIN.value}
        return self.index_template.render(params)

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET'])
    @cherrypy.tools.authenticate()
    @cherrypy.tools.authorize(role=UserRole.ADMIN)
    def new(self):
        devices = Device.enabled()
        return self.new_template.render({'devices': devices})

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET'])
    @cherrypy.tools.authenticate()
    @cherrypy.tools.authorize(role=UserRole.ADMIN)
    def edit(self, device_id: str):
        device = Device.find(int(device_id))
        devices = filter(lambda d: d.id != device.id, Device.enabled())
        return self.edit_template.render({'device': device, 'devices': devices})

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST'])
    @cherrypy.tools.authenticate()
    @cherrypy.tools.authorize(role=UserRole.ADMIN)
    def create(self, name: str, description: str, kind: str, options: str, dependent_device_id: str,
               dependent_start_delay: str, dependent_stop_delay: str, disabled: Optional[str] = None):
        device_type = DeviceType.cast(kind)
        dependent_device_id_value = None if dependent_device_id == '' else int(dependent_device_id)
        dependent_start_delay_value = None if dependent_start_delay == '' else int(dependent_start_delay)
        dependent_stop_delay_value = None if dependent_stop_delay == '' else int(dependent_stop_delay)
        Device(name=name, description=description, type=device_type, options=options, disabled=disabled == '1',
               dependent_device_id=dependent_device_id_value, dependent_start_delay=dependent_start_delay_value,
               dependent_stop_delay=dependent_stop_delay_value).save()
        raise cherrypy.HTTPRedirect("/devices")

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST'])
    @cherrypy.tools.authenticate()
    @cherrypy.tools.authorize(role=UserRole.ADMIN)
    def update(self, device_id: str, name: str, description: str, kind: str, options: str, dependent_device_id: str,
               dependent_start_delay: str, dependent_stop_delay: str, disabled: Optional[str] = None):
        device = Device.find(int(device_id))
        device.name = name
        device.description = description
        device.type = DeviceType.cast(kind)
        device.options = options
        device.disabled = disabled == '1'
        device.dependent_device_id = None if dependent_device_id == '' else int(dependent_device_id)
        device.dependent_start_delay = None if dependent_start_delay == '' else int(dependent_start_delay)
        device.dependent_stop_delay = None if dependent_stop_delay == '' else int(dependent_stop_delay)
        device.save()
        raise cherrypy.HTTPRedirect("/devices")

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET'])
    @cherrypy.tools.authenticate()
    @cherrypy.tools.authorize(role=UserRole.ADMIN)
    def destroy(self, device_id: str):
        Device.find(int(device_id)).destroy()
        raise cherrypy.HTTPRedirect("/devices")
