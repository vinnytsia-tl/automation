import os
import jinja2
import dotenv
import logging

from app.database import Database
from app.system.ldap import LDAP, LDAPConfig


class Config:
    production: bool = None
    log_directory: str = None
    log_level: str = None
    web_listen_host: str = None
    web_listen_port: int = None
    session_max_time: int = None
    database: Database = None
    ldap_descriptor: LDAP = None
    jinja_env: jinja2.Environment = None

    @staticmethod
    def load():
        dotenv.load_dotenv()

        Config.production = os.getenv('AUTOMATION_ENVIRONMENT') == 'production'
        Config.log_directory = os.getenv('LOG_DIR')
        Config.log_level = os.environ.get('LOG_LEVEL', logging.DEBUG)
        Config.web_listen_host = os.getenv('WEB_LISTEN_HOST')
        Config.web_listen_port = int(os.getenv('WEB_LISTEN_PORT'))
        Config.session_max_time = int(os.getenv('SESSION_MAX_TIME'))
        Config.database = Database(os.getenv('DATABASE_PATH'))
        Config.ldap_descriptor = LDAP(LDAPConfig.from_env())
        Config.jinja_env = jinja2.Environment(loader=jinja2.PackageLoader('app.web', 'www'))

        if not os.path.exists(Config.log_directory):
            os.mkdir(Config.log_directory)
