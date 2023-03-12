import sys

if sys.version_info < (3, 10):
    sys.exit('Python 3.10 or higher is required')

# pylint: disable=wrong-import-position
from app.config import Config
from app.service import RuleScheduler
from app.logging import setup_app_logger
# pylint: enable=wrong-import-position


if __name__ == '__main__':
    Config.load()
    setup_app_logger()
    RuleScheduler().run_forever()
