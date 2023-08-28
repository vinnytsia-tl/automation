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
    def index(self, device_id: Optional[str] = None, file_opt: Optional[str] = None,
              success: Optional[str] = None, error: Optional[str] = None,
              run_options: Optional[str] = ""):
        devices = Device.enabled()
        if file_opt is not None:
            run_options = f"file: '{file_opt}'"

        selected_device = Device.find(int(device_id)) if device_id else None

        return self.template.render({'success': success, 'error': error, 'devices': devices,
                                     'selected_device': selected_device, 'run_options': run_options})

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST'])
    @cherrypy.tools.authenticate()
    @cherrypy.tools.authorize(role=UserRole.RUNNER)
    def perform(self, action: str, device_id: str, run_options: str):
        exe_str = "SELECT username FROM sessions WHERE session_id = ?;"
        cursor = Config.database.execute(exe_str, (cherrypy.session.id,))
        username = cursor.fetchone()[0]
        logger.info('User %s requested action %s on device %s with options %s', username, action, device_id, run_options)
        command = {'action': action, 'device_id': int(device_id), 'run_options': run_options}
        response = {}
        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
                sock.connect(Config.command_socket_path.as_posix())
                sock.sendall(json.dumps(command).encode())
                response = json.loads(sock.recv(1024).decode())
        except Exception as err:  # pylint: disable=broad-except
            logger.error(repr(err))
            response['error'] = 'Помилка комунікації з rule scheduler'

        response['device_id'] = device_id
        response['run_options'] = run_options
        raise cherrypy.HTTPRedirect(f'/commands?{urlencode(response)}')
