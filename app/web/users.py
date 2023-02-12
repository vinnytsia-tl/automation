import cherrypy
from jinja2 import Environment, PackageLoader

from ..database import Database
from ..system.ldap import LDAP
from ..models import User, UserRole
from .functions import authenticate, authorize


class Users():
    def __init__(self, database: Database, ldap_descriptor: LDAP, session_max_time: int):
        self.database = database
        self.ldap_descriptor = ldap_descriptor
        self.session_max_time = session_max_time
        self.index_template = Environment(loader=PackageLoader('app.web', '')).get_template('www/users/index.html')

    @cherrypy.expose
    @authenticate
    @authorize()
    def index(self, role: UserRole):
        users = User.all(self.ldap_descriptor, self.database)
        params = {'users': users, 'showForm': role.value >= UserRole.ADMIN.value}
        return self.index_template.render(params)

    @cherrypy.expose
    @authenticate
    @authorize(role=UserRole.ADMIN)
    def update(self, _current_role: UserRole, login: str, role: str):
        user = User.find(self.ldap_descriptor, self.database, login)
        user.role = UserRole(int(role))
        user.save(self.database)
        raise cherrypy.HTTPRedirect("/users")
