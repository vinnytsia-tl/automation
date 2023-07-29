from app.common.config import Config as CommonConfig


class Config(CommonConfig):
    @staticmethod
    def load():
        super(Config, Config).load()
