from __future__ import annotations
from typing import Callable
import time
import inspect
import cherrypy

from app.models import UserRole
from app.database import Database
from app.config import Config


def is_authenticated():
    agent = cherrypy.request.headers.get('User-Agent')
    session_time = time.time() - Config.session_max_time
    exe_str = "SELECT 1 FROM sessions WHERE session_id = ? AND agent = ? AND time > ?;"
    cursor = Config.database.execute(exe_str, (cherrypy.session.id, agent, session_time))
    return cursor.fetchone() is not None


def authenticate(func: Callable):
    def wrapper(*args, **kwargs):
        if not is_authenticated():
            raise cherrypy.HTTPRedirect("/auth")
        return func(*args, **kwargs)

    return wrapper


def get_current_role():
    cursor = Config.database.execute('''
        SELECT role FROM users
        INNER JOIN sessions ON users.login = sessions.username
        WHERE session_id = ?
    ''', (cherrypy.session.id,))
    res = cursor.fetchone() or (0,)
    return UserRole(res[0])


def authorize(role_or_func: UserRole | Callable):
    if isinstance(role_or_func, UserRole):
        def wrapper(func: Callable):
            return __authorize_inner(role_or_func, func)
        return wrapper

    return __authorize_inner(UserRole.COMMON, role_or_func)


def __authorize_inner(role: UserRole, func: Callable):
    add_current_role = 'current_role' in inspect.getfullargspec(func).args

    def wrapper(*args, **kwargs):
        current_role = get_current_role()
        if current_role.value < role.value:
            raise cherrypy.HTTPRedirect("/home")
        if add_current_role:
            kwargs['current_role'] = current_role
        return func(*args, **kwargs)

    return wrapper
