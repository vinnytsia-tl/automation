import cherrypy

from app.web.utils import authenticate, authorize
from app.models import Rule, UserRole
from app.config import Config


class Rules():
    def __init__(self):
        self.index_template = Config.jinja_env.get_template('rules/index.html')
        self.new_template = Config.jinja_env.get_template('rules/new.html')

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET'])
    @authenticate
    @authorize
    def index(self):
        rules = Rule.all()
        params = {'rules': rules}
        return self.index_template.render(params)

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET'])
    @authenticate
    @authorize(UserRole.MODERATOR)
    def new(self):
        return self.new_template.render()

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST'])
    @authenticate
    @authorize(UserRole.MODERATOR)
    def create(self, name, description, device_id, start_time, duration):
        Rule(name=name, description=description, device_id=device_id, start_time=start_time, duration=duration).save()
        raise cherrypy.HTTPRedirect('/rules')
