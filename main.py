import os

from dotenv import load_dotenv

from app.database import Database
from app.system.ldap import LDAP, LDAPConfig
from app.web import Web


load_dotenv()

LDAP_CONFIG = LDAPConfig.from_env()

WEB_LISTEN_HOST = os.getenv("WEB_LISTEN_HOST")
WEB_LISTEN_PORT = int(os.getenv("WEB_LISTEN_PORT"))
LOG_DIR = os.getenv("LOG_DIR")
DATABASE_PATH = os.getenv("DATABASE_PATH")
SESSION_MAX_TIME = int(os.getenv("SESSION_MAX_TIME"))

APP_ENVIRONMENT = os.getenv("AUTOMATION_ENVIRONMENT")
if APP_ENVIRONMENT is None:
    APP_ENVIRONMENT = "development"

if __name__ == "__main__":
    database = Database(DATABASE_PATH)
    ldap_descriptor = LDAP(LDAP_CONFIG)
    Web.start(APP_ENVIRONMENT, WEB_LISTEN_HOST, WEB_LISTEN_PORT, LOG_DIR, SESSION_MAX_TIME, database, ldap_descriptor)
