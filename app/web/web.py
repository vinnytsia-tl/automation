import os
import cherrypy

from app.config import Config
from .controllers import Auth, Devices, Home, Root, Rules, Users

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
    def start():
        app = Root()
        app.auth = Auth()
        app.home = Home()
        app.devices = Devices()
        app.rules = Rules()
        app.users = Users()

        cherrypy.config.update({
            'server.socket_host': Config.web_listen_host,
            'server.socket_port': Config.web_listen_port,
            'engine.autoreload.on': not Config.production,
            'engine.autoreload.frequency': 1,
            'log.screen': not Config.production,
            'log.error_file': Config.log_directory + '/web_error.log',
            'log.access_file': Config.log_directory + '/web_access.log',
        })

        if Config.production:
            CHERRYPY_CONFIG['/']['tools.sessions.secure'] = True

        cherrypy.engine.subscribe('start', Config.database.cleanup)
        cherrypy.tree.mount(app, '/', CHERRYPY_CONFIG)
        cherrypy.engine.start()
        cherrypy.engine.block()

    @staticmethod
    @cherrypy.tools.register('before_finalize', priority=60)
    def secureheaders():
        headers = cherrypy.response.headers
        headers['X-Frame-Options'] = 'DENY'
        headers['X-XSS-Protection'] = '1; mode=block'
        if Config.production:
            headers['Content-Security-Policy'] = "default-src 'self' https;"
