import logging

import cherrypy

from app.config import Config
from app.models import UserRole

logger = logging.getLogger(__name__)


def get_current_role():
    cursor = Config.database.execute('''
        SELECT role FROM users
        INNER JOIN sessions ON users.login = sessions.username
        WHERE session_id = ?
    ''', (cherrypy.session.id,))
    res = cursor.fetchone() or (0,)
    return UserRole(res[0])


def authorize(role: UserRole = UserRole.COMMON):
    current_role = get_current_role()
    if current_role.value < role.value:
        logger.debug('User is not authorized (role is %s, required %s), redirecting to /home', current_role, role)
        raise cherrypy.HTTPRedirect("/home")
    cherrypy.session['current_role'] = current_role


def init_hooks():
    cherrypy.tools.authorize = cherrypy.Tool('before_handler', authorize)
