from app.web import Web
from app.config import Config
from app.database.migrations import apply_migrations

if __name__ == '__main__':
    Config.load()
    apply_migrations()
    Web.start()
