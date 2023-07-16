import logging

from pygame import mixer

from .device import Device

FADEOUT_TIME = 2000
logger = logging.getLogger(__name__)


class Audio(Device):
    def __init__(self, file: str):
        mixer.init(buffer=1024)
        self.sound = mixer.Sound(file)
        logger.info('Audio initialized for file %s', file)

    def start(self):
        super().start()
        self.sound.play()

    def stop(self, force: bool = False):
        super().stop()
        if force:
            self.sound.stop()
        else:
            self.sound.fadeout(FADEOUT_TIME)

    def destroy(self):
        super().destroy()
        del self.sound
        mixer.quit()

    @property
    def stop_delay(self) -> int:
        return FADEOUT_TIME
