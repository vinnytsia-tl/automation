import os

from dotenv import load_dotenv

from app.database import Database
from app.system.ldap import LDAP
from app.web import Web


load_dotenv()

LDAP_SERVER = os.getenv("LDAP_SERVER")
LDAP_PORT = int(os.getenv("LDAP_PORT"))
LDAP_USE_SSL = bool(os.getenv("LDAP_USE_SSL"))
LDAP_BIND_USER = os.getenv("LDAP_BIND_USER")
LDAP_BIND_PASSWORD = os.getenv("LDAP_BIND_PASSWORD")

WEB_LISTEN_HOST = os.getenv("WEB_LISTEN_HOST")
WEB_LISTEN_PORT = int(os.getenv("WEB_LISTEN_PORT"))
LOG_DIR = os.getenv("LOG_DIR")
DATABASE_PATH = os.getenv("DATABASE_PATH")
SESSION_MAX_TIME = int(os.getenv("SESSION_MAX_TIME"))

if __name__ == "__main__":
    database = Database(DATABASE_PATH)
    ldap_descriptor = LDAP(LDAP_SERVER, LDAP_PORT, LDAP_USE_SSL, LDAP_BIND_USER, LDAP_BIND_PASSWORD)
    Web.start(WEB_LISTEN_HOST, WEB_LISTEN_PORT, LOG_DIR, SESSION_MAX_TIME, database, ldap_descriptor)
