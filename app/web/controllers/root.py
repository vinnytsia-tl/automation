import logging

import cherrypy

from app.common.web.utils import is_authenticated

from .audio_files import AudioFiles
from .auth import Auth
from .commands import Commands
from .devices import Devices
from .home import Home
from .rule_scheduler import RuleScheduler
from .rules import Rules
from .users import Users

logger = logging.getLogger(__name__)


class Root():
    def __init__(self) -> None:
        self.auth = Auth()
        self.home = Home()
        self.devices = Devices()
        self.rules = Rules()
        self.users = Users()
        self.rule_scheduler = RuleScheduler()
        self.audio_files = AudioFiles()
        self.commands = Commands()
        logger.debug("Created app controllers")

    @cherrypy.expose
    def index(self):
        raise cherrypy.HTTPRedirect("/home" if is_authenticated() else "/auth")
