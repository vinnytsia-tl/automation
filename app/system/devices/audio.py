import logging

from pygame import mixer

from .device import Device

logger = logging.getLogger(__name__)


class Audio(Device):
    def __init__(self, file: str):
        mixer.init(buffer=1024)
        self.sound = mixer.Sound(file)
        logger.info('Audio initialized for file %s', file)

    def start(self):
        self.sound.play()

    def stop(self):
        self.sound.stop()

    def destroy(self):
        del self.sound
        mixer.quit()
