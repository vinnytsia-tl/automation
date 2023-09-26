from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import yaml
from pygame import mixer

from app.config import Config

from .device import Device

FADEOUT_TIME = 2000
logger = logging.getLogger(__name__)


@dataclass
class AudioRunOptions:
    file: Path
    fadeout: int
    volume: int

    def __init__(self, data: dict):
        self.__set_file(data.get('file', None))
        self.__set_fadeout(data.get('fadeout', FADEOUT_TIME))
        self.__set_volume(data.get('volume', 100))

    def __set_file(self, file: Any):
        if not isinstance(file, str) or file == '':
            raise ValueError("Обов'язковий параметр file - відсутній")
        self.file = Path(file)
        if not self.file.is_absolute():
            self.file = Config.audio_folder.joinpath(self.file).resolve()
        if not self.file.is_file():
            raise ValueError("Вказаний файл не існує")

    def __set_fadeout(self, fadeout: Any):
        if not isinstance(fadeout, int):
            raise ValueError("Параметр fadeout - має бути число")
        self.fadeout = fadeout

    def __set_volume(self, volume: Any):
        if not isinstance(volume, int) or volume < 0 or volume > 100:
            raise ValueError("Параметр volume - має бути число від 0 до 100")
        self.volume = volume


class Audio(Device):
    def __init__(self):
        super().__init__()
        mixer.init(buffer=1024)
        self.sounds = dict[Path, mixer.Sound]()

    def parse_run_options(self, run_options: Optional[str]) -> AudioRunOptions:
        if not isinstance(run_options, str):
            raise ValueError("Параметри відсутні")
        opts = yaml.safe_load(run_options)
        if not isinstance(opts, dict):
            raise ValueError("Помилка читання параметрів")
        return AudioRunOptions(opts)

    def key(self, run_options: AudioRunOptions) -> Path:
        return run_options.file

    def stop_delay(self, run_options: AudioRunOptions) -> float:
        return run_options.fadeout / 1000

    def preload(self, run_options: AudioRunOptions):
        super().preload(run_options)
        if run_options.file not in self.sounds:
            self.sounds[run_options.file] = mixer.Sound(run_options.file)
            logger.debug('Loaded sound file %s', run_options.file)
        else:
            logger.debug('Sound file %s already loaded', run_options.file)

    def start(self, run_options: AudioRunOptions):
        super().start(run_options)
        self.sounds[run_options.file].play()
        self.sounds[run_options.file].set_volume(run_options.volume / 100)
        logger.debug('Playing sound file %s with volume %d', run_options.file, run_options.volume)

    def stop(self, run_options: AudioRunOptions):
        super().stop(run_options)
        self.sounds[run_options.file].fadeout(run_options.fadeout)
        logger.debug('Fading out sound file %s for %s ms', run_options.file, run_options.fadeout)

    def destroy(self):
        super().destroy()
        for sound in self.sounds.values():
            sound.stop()
        self.sounds.clear()
        mixer.quit()
