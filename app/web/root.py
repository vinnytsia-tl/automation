import cherrypy

from .functions import authorized


class Root():
    def __init__(self, database, session_max_time):
        self.database = database
        self.session_max_time = session_max_time

    @cherrypy.expose
    def index(self):
        raise cherrypy.HTTPRedirect("/home" if authorized(self.database, self.session_max_time) else "/auth")
