from pathlib import Path

from app.common.config import Config as CommonConfig
from app.common.config.utils import getenv_typed


class Config(CommonConfig):
    audio_folder: Path
    command_socket_path: Path

    @staticmethod
    def load():
        super(Config, Config).load()
        Config.audio_folder = getenv_typed('AUDIO_FOLDER', Path)
        Config.audio_folder.mkdir(parents=True, exist_ok=True)
        Config.command_socket_path = getenv_typed('COMMAND_SOCKET_PATH', Path)
