import cherrypy

from app.web.utils import authenticate, authorize
from app.models import User, UserRole
from app.config import Config


class Users():
    def __init__(self):
        self.index_template = Config.jinja_env.get_template('users/index.html')

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET'])
    @authenticate
    @authorize
    def index(self, current_role: UserRole):
        users = User.all()
        params = {'users': users, 'showForm': current_role.value >= UserRole.ADMIN.value}
        return self.index_template.render(params)

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST'])
    @authenticate
    @authorize(UserRole.ADMIN)
    def update(self, login: str, role: str):
        user = User.find(login)
        user.role = UserRole(int(role))
        user.save()
        raise cherrypy.HTTPRedirect("/users")
