import cherrypy

from app.config import Config
from app.models import User, UserRole


class Users():
    def __init__(self):
        self.index_template = Config.jinja_env.get_template('users/index.html')

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET'])
    @cherrypy.tools.authenticate()
    @cherrypy.tools.authorize()
    def index(self):
        current_role = UserRole(cherrypy.session['current_role'])
        users = User.all()
        params = {'users': users, 'showForm': current_role.value >= UserRole.ADMIN.value, 'roles': UserRole}
        return self.index_template.render(params)

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST'])
    @cherrypy.tools.authenticate()
    @cherrypy.tools.authorize(role=UserRole.ADMIN)
    def update(self, login: str, role: str):
        user = User.find(login)
        user.role = UserRole(int(role))
        user.save()
        raise cherrypy.HTTPRedirect("/users")
