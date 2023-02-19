import time
import cherrypy

from app.web.utils import is_authenticated, authenticate
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
    def login(self, username, password):
        if is_authenticated():
            raise cherrypy.HTTPRedirect("/home")

        if not Config.ldap_descriptor.login(username, password):
            return self.template.render(errors=["Неправильний логін або пароль"])

        with Config.database.get_connection() as connection:
            cursor = connection.cursor()
            agent = cherrypy.request.headers.get('User-Agent')
            session_time = time.time()
            exe_str = "DELETE FROM sessions WHERE username = ? OR session_id = ?;"
            cursor.execute(exe_str, [username, cherrypy.session.id])
            exe_str = "INSERT INTO sessions(session_id, username, agent, time) values(?, ?, ?, ?);"
            cursor.execute(exe_str, [cherrypy.session.id, username, agent, session_time])

        cherrypy.session['username'] = username
        raise cherrypy.HTTPRedirect("/home")

    @cherrypy.expose
    @authenticate
    def logout(self):
        with Config.database.get_connection() as connection:
            connection.execute('DELETE FROM sessions WHERE session_id = ?;', (cherrypy.session.id,))

        cherrypy.session['username'] = None
        raise cherrypy.HTTPRedirect("/auth")
