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

    def __init__(self, data: dict):
        self.__set_file(data['file'])
        self.__set_fadeout(data.get('fadeout', FADEOUT_TIME))

    def __set_file(self, file: Any):
        assert isinstance(file, str)
        self.file = Path(file)
        if not self.file.is_absolute():
            self.file = Config.audio_folder.joinpath(self.file).resolve()

    def __set_fadeout(self, fadeout: Any):
        assert isinstance(fadeout, int)
        self.fadeout = fadeout


class Audio(Device):
    def __init__(self):
        mixer.init(buffer=1024)
        self.sounds = dict[Path, mixer.Sound]()

    def parse_run_options(self, run_options: Optional[str]) -> AudioRunOptions:
        assert isinstance(run_options, str)
        opts = yaml.safe_load(run_options)
        assert isinstance(opts, dict)
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
        logger.debug('Playing sound file %s', run_options.file)

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
