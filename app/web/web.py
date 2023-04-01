import logging
import os

import cherrypy

from app.config import Config

from .controllers import Root

logger = logging.getLogger(__name__)

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
        logger.info('Starting web server...')

        cherrypy.config.update({
            'server.socket_host': Config.web_listen_host,
            'server.socket_port': Config.web_listen_port,
            'server.thread_pool': Config.web_thread_pool,
            'engine.autoreload.on': not Config.production,
            'engine.autoreload.frequency': 1,
            'log.screen': not Config.production,
            'log.screen.level': Config.log_level,
            'log.error_file': Config.log_directory + '/web_error.log',
            'log.access_file': Config.log_directory + '/web_access.log',
        })
        logger.debug('Web server config updated.')

        if Config.production:
            CHERRYPY_CONFIG['/']['tools.sessions.secure'] = True

        cherrypy.engine.subscribe('start', Config.database.cleanup)
        logger.debug('Web engine subscribed.')
        cherrypy.tree.mount(Root(), '/', CHERRYPY_CONFIG)
        logger.debug('Web tree mounted.')
        cherrypy.engine.start()
        logger.info('Web server started.')
        cherrypy.engine.block()

    @staticmethod
    @cherrypy.tools.register('before_finalize', priority=60)
    def secureheaders():
        logger.debug('Execute secureheaders hook')

        headers = cherrypy.response.headers
        headers['X-Frame-Options'] = 'DENY'
        headers['X-XSS-Protection'] = '1; mode=block'
        if Config.production:
            headers['Content-Security-Policy'] = "default-src 'self' https;"
