import cherrypy

from app.config import Config
from app.models import Device, Rule, UserRole
from app.models.rule import parse_duration
from app.web.utils import authenticate, authorize


class Rules():
    def __init__(self):
        self.index_template = Config.jinja_env.get_template('rules/index.html')
        self.new_template = Config.jinja_env.get_template('rules/new.html')
        self.edit_template = Config.jinja_env.get_template('rules/edit.html')

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET'])
    @authenticate
    @authorize
    def index(self, current_role: UserRole):
        rules = Rule.all_start_order()
        params = {'rules': rules, 'isModerator': current_role.value >= UserRole.MODERATOR.value}
        return self.index_template.render(params)

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET'])
    @authenticate
    @authorize(UserRole.MODERATOR)
    def new(self):
        devices = Device.all()
        return self.new_template.render({'devices': devices})

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET'])
    @authenticate
    @authorize(UserRole.MODERATOR)
    def edit(self, rule_id: int):
        rule = Rule.find(rule_id)
        devices = Device.all()
        return self.edit_template.render({'rule': rule, 'devices': devices})

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST'])
    @authenticate
    @authorize(UserRole.MODERATOR)
    def create(self, name, description, device_id, start_time, duration):
        start_time = parse_duration(start_time)
        duration = parse_duration(duration)
        Rule(name=name, description=description, device_id=device_id, start_time=start_time, duration=duration).save()
        raise cherrypy.HTTPRedirect('/rules')

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST'])
    @authenticate
    @authorize(UserRole.MODERATOR)
    def update(self, rule_id, name, description, device_id, start_time, duration):
        rule = Rule.find(rule_id)
        rule.name = name
        rule.description = description
        rule.device_id = int(device_id)
        rule.start_time = parse_duration(start_time)
        rule.duration = parse_duration(duration)
        rule.save()
        raise cherrypy.HTTPRedirect('/rules')

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET'])
    @authenticate
    @authorize(UserRole.MODERATOR)
    def destroy(self, rule_id: int):
        Rule.find(rule_id).destroy()
        raise cherrypy.HTTPRedirect('/rules')
