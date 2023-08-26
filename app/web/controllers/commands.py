import json
import logging
import socket
from typing import Optional
from urllib.parse import urlencode

import cherrypy

from app.config import Config
from app.models import Device, UserRole

logger = logging.getLogger(__name__)


class Commands():
    def __init__(self):
        self.template = Config.jinja_env.get_template('commands/index.html')

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET'])
    @cherrypy.tools.authenticate()
    @cherrypy.tools.authorize(role=UserRole.RUNNER)
    def index(self, success: Optional[str] = None, error: Optional[str] = None):
        devices = Device.enabled()
        return self.template.render({'success': success, 'error': error, 'devices': devices})

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST'])
    @cherrypy.tools.authenticate()
    @cherrypy.tools.authorize(role=UserRole.RUNNER)
    def perform(self, action: str, device_id: str, run_options: str):
        command = {'action': action, 'device_id': int(device_id), 'run_options': run_options}
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
            sock.connect(Config.command_socket_path.as_posix())
            sock.sendall(json.dumps(command).encode())
            response = json.loads(sock.recv(1024).decode())
        raise cherrypy.HTTPRedirect(f'/commands?{urlencode(response)}')
