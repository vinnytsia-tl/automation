import sys

if sys.version_info < (3, 10):
    sys.exit('Python 3.10 or higher is required')

# pylint: disable=wrong-import-position
from app.web import Web
from app.config import Config
from app.database.migrations import apply_migrations
from app.logging import setup_app_logger
# pylint: enable=wrong-import-position


if __name__ == '__main__':
    Config.load()
    setup_app_logger()
    apply_migrations()
    Web.start()
