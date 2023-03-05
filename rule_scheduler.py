from app.config import Config
from app.service import RuleScheduler
from app.logging import setup_app_logger


if __name__ == '__main__':
    Config.load()
    setup_app_logger()
    RuleScheduler().run_forever()
