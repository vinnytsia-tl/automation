import time

import cherrypy
from jinja2 import Environment, PackageLoader

from .functions import is_authenticated, authenticate


class Auth():
    def __init__(self, database, session_max_time, ldap_descriptor):
        self.database = database
        self.session_max_time = session_max_time
        self.ldap_descriptor = ldap_descriptor
        self.template = Environment(loader=PackageLoader('app.web', '')).get_template('www/auth/index.html')

    @cherrypy.expose
    def index(self):
        if is_authenticated(self.database, self.session_max_time):
            raise cherrypy.HTTPRedirect("/home")

        return self.template.render()

    @cherrypy.expose
    def login(self, username, password):
        if is_authenticated(self.database, self.session_max_time):
            raise cherrypy.HTTPRedirect("/home")

        if not self.ldap_descriptor.login(username, password):
            return self.template.render(errors=["Неправильний логін або пароль"])

        cursor = self.database.cursor()
        agent = cherrypy.request.headers.get('User-Agent')
        session_time = time.time()
        exe_str = "DELETE FROM sessions WHERE username = ? OR session_id = ?;"
        cursor.execute(exe_str, [username, cherrypy.session.id])
        exe_str = "INSERT INTO sessions(session_id, username, agent, time) values(?, ?, ?, ?);"
        cursor.execute(exe_str, [cherrypy.session.id, username, agent, session_time])

        self.database.commit()

        cherrypy.session['username'] = username

        raise cherrypy.HTTPRedirect("/home")

    @cherrypy.expose
    @authenticate
    def logout(self):
        cursor = self.database.cursor()
        exe_str = "DELETE FROM sessions WHERE session_id = ?;"
        cursor.execute(exe_str, [cherrypy.session.id])
        self.database.commit()

        cherrypy.session['username'] = None

        raise cherrypy.HTTPRedirect("/auth")
