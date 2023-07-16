import logging

from . import GPIO

logger = logging.getLogger(__name__)


class GPIOLowLevel(GPIO):
    def __init__(self, port: int):
        GPIO.__init__(self, port)

    def start(self):
        super().start()
        self.__write_param__('value', '0')

    def stop(self, force: bool = False):
        super().stop()
        self.__write_param__('value', '1')
