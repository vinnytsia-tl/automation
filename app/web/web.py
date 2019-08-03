import os

import cherrypy

from .root import Root
from .auth import Auth
from .home import Home


CHERRYPY_CONFIG = {
    '/': {
        'tools.secureheaders.on': True,
        'tools.sessions.on': True,
        'tools.sessions.httponly': True,
        'tools.staticdir.root': os.path.abspath(os.getcwd()) + '/app/web',
        'tools.trailing_slash.on': False,
        'tools.response_headers.on': True,
    },
    '/static': {
        'tools.staticdir.on': True,
        'tools.staticdir.dir': './static',
    },
}


class Web:
    @staticmethod
    def start(host, port, log_dir, session_max_time, database, ldap_descriptor):
        app = Root(database, session_max_time)
        app.auth = Auth(database, session_max_time, ldap_descriptor)
        app.home = Home(database, session_max_time)

        if not os.path.exists(log_dir):
            os.mkdir(log_dir)

        cherrypy.config.update({
            'server.socket_host': host,
            'server.socket_port': port,
            'engine.autoreload_on': False,
            'log.screen': False,
            'log.error_file': log_dir + '/web_error.log',
            'log.access_file': log_dir + '/web_access.log',
        })

        cherrypy.engine.subscribe('start', database.cleanup)
        cherrypy.tree.mount(app, '/', CHERRYPY_CONFIG)
        cherrypy.engine.start()

    @staticmethod
    @cherrypy.tools.register('before_finalize', priority=60)
    def secureheaders():
        headers = cherrypy.response.headers
        headers['X-Frame-Options'] = 'DENY'
        headers['X-XSS-Protection'] = '1; mode=block'
        # headers['Content-Security-Policy'] = "default-src 'self' https;"
