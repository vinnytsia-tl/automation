import logging

from pygame import mixer

from .device import Device

logger = logging.getLogger(__name__)


class Audio(Device):
    def __init__(self, file: str):
        self.file = file
        mixer.init()
        logger.info('Audio initialized for file %s', file)

    def start(self):
        mixer.music.load(self.file)
        mixer.music.play()

    def stop(self):
        mixer.music.stop()
        mixer.music.unload()

    def destroy(self):
        mixer.quit()
