import os

import dotenv
import jinja2

from app.database import Database
from app.system.ldap import LDAP, LDAPConfig

from .utils import getenv, getenv_typed


class Config:
    production: bool
    log_directory: str
    log_file: str
    log_level: str
    web_listen_host: str
    web_listen_port: int
    web_thread_pool: int
    session_max_time: int
    database: Database
    ldap_descriptor: LDAP
    jinja_env: jinja2.Environment

    @staticmethod
    def load():
        dotenv.load_dotenv(override=False)

        Config.production = getenv('AUTOMATION_ENVIRONMENT', 'development') == 'production'
        Config.log_directory = getenv('LOG_DIR')
        Config.log_file = getenv('LOG_FILE')
        Config.log_level = getenv('LOG_LEVEL', 'DEBUG')
        Config.web_listen_host = getenv('WEB_LISTEN_HOST')
        Config.web_listen_port = getenv_typed('WEB_LISTEN_PORT', int)
        Config.web_thread_pool = getenv_typed('WEB_THREAD_POOL_SIZE', int, 10)
        Config.session_max_time = getenv_typed('SESSION_MAX_TIME', int)
        Config.database = getenv_typed('DATABASE_PATH', Database)
        Config.ldap_descriptor = LDAP(LDAPConfig.from_env())
        Config.jinja_env = jinja2.Environment(loader=jinja2.PackageLoader('app.web', 'www'))

        if not os.path.exists(Config.log_directory):
            os.mkdir(Config.log_directory)
