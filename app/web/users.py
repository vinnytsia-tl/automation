import cherrypy
from jinja2 import Environment, PackageLoader

from ..models import User


class Users():
    def __init__(self, database, ldap_descriptor):
        self.database = database
        self.ldap_descriptor = ldap_descriptor
        self.index_template = Environment(loader=PackageLoader('app.web', '')).get_template('www/users/index.html')

    @cherrypy.expose
    def index(self):
        users = User.all(self.ldap_descriptor, self.database)
        params = {'users': users}
        return self.index_template.render(params)
