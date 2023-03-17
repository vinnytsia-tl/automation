import logging
import os

import dotenv
import jinja2

from app.database import Database
from app.system.ldap import LDAP, LDAPConfig


class Config:
    production: bool
    log_directory: str
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

        Config.production = os.getenv('AUTOMATION_ENVIRONMENT') == 'production'
        Config.log_directory = os.getenv('LOG_DIR')
        Config.log_file = os.getenv('LOG_FILE')
        Config.log_level = os.environ.get('LOG_LEVEL', logging.DEBUG)
        Config.web_listen_host = os.getenv('WEB_LISTEN_HOST')
        Config.web_listen_port = int(os.getenv('WEB_LISTEN_PORT'))
        Config.web_thread_pool = int(os.getenv('WEB_THREAD_POOL_SIZE', '10'))
        Config.session_max_time = int(os.getenv('SESSION_MAX_TIME'))
        Config.database = Database(os.getenv('DATABASE_PATH'))
        Config.ldap_descriptor = LDAP(LDAPConfig.from_env())
        Config.jinja_env = jinja2.Environment(loader=jinja2.PackageLoader('app.web', 'www'))

        if not os.path.exists(Config.log_directory):
            os.mkdir(Config.log_directory)
