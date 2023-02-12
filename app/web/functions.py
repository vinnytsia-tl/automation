from __future__ import annotations
from typing import Callable
import time
import cherrypy

from ..models import UserRole
from ..database import Database


def is_authenticated(database, session_max_time):
    cursor = database.cursor()
    agent = cherrypy.request.headers.get('User-Agent')
    session_time = time.time() - session_max_time
    exe_str = "SELECT 1 FROM sessions WHERE session_id = ? AND agent = ? AND time > ?;"
    res = cursor.execute(exe_str, [cherrypy.session.id, agent, session_time])

    return res.fetchone() is not None


def authenticate(func: Callable):
    def wrapper(self, *args):
        if not is_authenticated(self.database, self.session_max_time):
            raise cherrypy.HTTPRedirect("/auth")
        return func(self, *args)

    return wrapper


def get_current_role(database: Database):
    cursor = database.cursor()
    cursor.execute('''
        SELECT role FROM users
        INNER JOIN sessions ON users.login = sessions.username
        WHERE session_id = ?
    ''', (cherrypy.session.id,))
    res = cursor.fetchone() or (0,)
    return UserRole(res[0])


def authorize(role: UserRole = UserRole.COMMON):
    def wrap(func: Callable):
        def wrapper(self, *args):
            current_role = get_current_role(self.database)
            if current_role.value < role.value:
                raise cherrypy.HTTPRedirect("/home")
            return func(self, current_role, *args)
        return wrapper
    return wrap
