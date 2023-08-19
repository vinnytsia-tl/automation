import sys

if sys.version_info < (3, 10):
    sys.exit('Python 3.10 or higher is required')

# pylint: disable=wrong-import-position

import pygame

from app.config import Config
from app.service import RuleScheduler, ensure_ntp_sync

# pylint: enable=wrong-import-position


if __name__ == '__main__':
    pygame.init()
    Config.load()
    Config.setup_app_logger()
    ensure_ntp_sync()
    RuleScheduler().run_forever()
