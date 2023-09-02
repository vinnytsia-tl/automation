import json
import logging
import socket

import cherrypy
from pystemd.systemd1 import Unit

from app.config import Config
from app.models import RuleStateEntry, UserRole

SERVICE_NAME = b'rule-scheduler.service'

#
# Start, Stop, Reload, Restart - mode
# The mode needs to be one of "replace", "fail", "isolate", "ignore-dependencies", or "ignore-requirements".
# If "replace", the method will start the unit and its dependencies,
# possibly replacing already queued jobs that conflict with it.
#
# Kill - whom, signal
# The who enum is one of "main", "control" or "all".
# If "main", only the main process of the unit is killed.
# The signal argument is a signal number.
#
ACTIONS = {
    'Start': (b'replace',),
    'Stop': (b'replace',),
    'Kill': (b'all', 9),
    'Reload': (b'replace',),
    'Restart': (b'replace',)
}

logger = logging.getLogger(__name__)


class RuleScheduler():
    def __init__(self):
        self.template = Config.jinja_env.get_template('rule_scheduler/index.html')

    def __fetch_rule_states(self) -> list[RuleStateEntry]:
        try:
            logger.debug('Fetching rule states')
            command = {'action': 'status'}
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
                sock.connect(Config.command_socket_path.as_posix())
                sock.sendall(json.dumps(command).encode())
                data = sock.recv(1024).decode()
                logger.debug('Received data: %s', data)
                response = json.loads(data)
            if not isinstance(response, list):
                logger.error('Bad response from rule scheduler: %s', response)
                return []
            return [RuleStateEntry.from_json(entry) for entry in response]
        except Exception as err:  # pylint: disable=broad-except
            logger.error(repr(err))
            return []

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET'])
    @cherrypy.tools.authenticate()
    @cherrypy.tools.authorize(role=UserRole.ADMIN)
    def index(self):
        unit = Unit(SERVICE_NAME)
        unit.load()
        color = 'green' if unit.Unit.ActiveState == b'active' else 'red'
        rule_states = self.__fetch_rule_states()
        return self.template.render({'color': color,
                                     'state': unit.Unit.ActiveState.decode(),
                                     'pid': unit.Service.MainPID,
                                     'actions': ACTIONS.keys(),
                                     'rule_states': rule_states})

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET'])
    @cherrypy.tools.authenticate()
    @cherrypy.tools.authorize(role=UserRole.ADMIN)
    def perform(self, action: str):
        if action not in ACTIONS:
            raise cherrypy.HTTPError(400, 'Invalid action')
        unit = Unit(SERVICE_NAME)
        unit.load()
        getattr(unit.Unit, action)(*ACTIONS[action])
        raise cherrypy.HTTPRedirect('/rule_scheduler')
