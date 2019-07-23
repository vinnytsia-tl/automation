import time

import cherrypy


def authorized(database, session_max_time):
    cursor = database.cursor()
    agent = cherrypy.request.headers.get('User-Agent')
    session_time = time.time() - session_max_time
    exe_str = "SELECT 1 FROM sessions WHERE session_id = ? AND agent = ? AND time > ?;"
    res = cursor.execute(exe_str, [cherrypy.session.id, agent, session_time])

    return res.fetchone() is not None
