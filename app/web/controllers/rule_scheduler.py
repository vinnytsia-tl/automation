import cherrypy
from pystemd.systemd1 import Unit

from app.config import Config
from app.models import UserRole

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


class RuleScheduler():
    def __init__(self):
        self.template = Config.jinja_env.get_template('rule_scheduler/index.html')

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET'])
    @cherrypy.tools.authenticate()
    @cherrypy.tools.authorize(role=UserRole.ADMIN)
    def index(self):
        unit = Unit(SERVICE_NAME)
        unit.load()
        color = 'green' if unit.Unit.ActiveState == b'active' else 'red'
        return self.template.render({'color': color,
                                     'state': unit.Unit.ActiveState.decode(),
                                     'pid': unit.Service.MainPID,
                                     'actions': ACTIONS.keys()})

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
