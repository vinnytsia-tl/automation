import cherrypy

from app.config import Config
from app.models import Device, Rule, UserRole
from app.models.rule import DayOfWeek, parse_duration


class Rules():
    def __init__(self):
        self.index_template = Config.jinja_env.get_template('rules/index.html')
        self.new_template = Config.jinja_env.get_template('rules/new.html')
        self.edit_template = Config.jinja_env.get_template('rules/edit.html')

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET'])
    @cherrypy.tools.authenticate()
    @cherrypy.tools.authorize()
    def index(self):
        current_role = UserRole(cherrypy.session['current_role'])
        rules = Rule.all_start_order()
        params = {'rules': rules, 'isModerator': current_role.value >= UserRole.MODERATOR.value, 'DayOfWeek': DayOfWeek}
        return self.index_template.render(params)

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET'])
    @cherrypy.tools.authenticate()
    @cherrypy.tools.authorize(role=UserRole.MODERATOR)
    def new(self):
        devices = Device.all()
        return self.new_template.render({'devices': devices, 'DayOfWeek': DayOfWeek})

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET'])
    @cherrypy.tools.authenticate()
    @cherrypy.tools.authorize(role=UserRole.MODERATOR)
    def edit(self, rule_id: str):
        rule = Rule.find(int(rule_id))
        devices = Device.all()
        return self.edit_template.render({'rule': rule, 'devices': devices, 'DayOfWeek': DayOfWeek})

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST'])
    @cherrypy.tools.authenticate()
    @cherrypy.tools.authorize(role=UserRole.MODERATOR)
    def create(self, name: str, description: str, device_id: str, start_time: str, duration: str,
               days_of_week: str | list[str]):
        rule = Rule(name=name, description=description, device_id=int(device_id))
        rule.start_time = parse_duration(start_time)
        rule.duration = parse_duration(duration)
        if isinstance(days_of_week, str):
            rule.days_of_week = DayOfWeek.cast(days_of_week)
        else:
            rule.days_of_week = DayOfWeek.cast(sum(map(int, days_of_week)))
        rule.save()
        raise cherrypy.HTTPRedirect('/rules')

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST'])
    @cherrypy.tools.authenticate()
    @cherrypy.tools.authorize(role=UserRole.MODERATOR)
    def update(self, rule_id: str, name: str, description: str, device_id: str, start_time: str, duration: str,
               days_of_week: str | list[str]):
        rule = Rule.find(int(rule_id))
        rule.name = name
        rule.description = description
        rule.device_id = int(device_id)
        rule.start_time = parse_duration(start_time)
        rule.duration = parse_duration(duration)
        if isinstance(days_of_week, str):
            rule.days_of_week = DayOfWeek.cast(days_of_week)
        else:
            rule.days_of_week = DayOfWeek.cast(sum(map(int, days_of_week)))
        rule.save()
        raise cherrypy.HTTPRedirect('/rules')

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET'])
    @cherrypy.tools.authenticate()
    @cherrypy.tools.authorize(role=UserRole.MODERATOR)
    def destroy(self, rule_id: str):
        Rule.find(int(rule_id)).destroy()
        raise cherrypy.HTTPRedirect('/rules')
