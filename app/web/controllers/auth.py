import cherrypy

from app.common.web.utils import is_authenticated, save_session
from app.config import Config


class Auth():
    def __init__(self):
        self.template = Config.jinja_env.get_template('auth/index.html')

    @cherrypy.expose
    def index(self):
        if is_authenticated():
            raise cherrypy.HTTPRedirect("/home")

        return self.template.render()

    @cherrypy.expose
    def login(self, username: str, password: str):
        if is_authenticated():
            raise cherrypy.HTTPRedirect("/home")

        if not Config.ldap_descriptor.login(username, password):
            return self.template.render(errors=["Неправильний логін або пароль"])

        save_session(username)

        cherrypy.session['username'] = username
        raise cherrypy.HTTPRedirect("/home")

    @cherrypy.expose
    @cherrypy.tools.authenticate()
    def logout(self):
        with Config.database.get_connection() as connection:
            connection.execute('DELETE FROM sessions WHERE session_id = ?;', (cherrypy.session.id,))

        cherrypy.session['username'] = None
        cherrypy.session['current_role'] = None
        raise cherrypy.HTTPRedirect("/auth")
