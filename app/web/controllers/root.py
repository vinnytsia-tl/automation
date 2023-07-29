import logging

import cherrypy

from app.common.web.utils import is_authenticated

from .auth import Auth
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
        logger.debug("Created app controlers")

    @cherrypy.expose
    def index(self):
        raise cherrypy.HTTPRedirect("/home" if is_authenticated() else "/auth")
