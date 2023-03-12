import logging

from . import GPIO

logger = logging.getLogger(__name__)


class GPIOLowLevel(GPIO):
    def __init__(self, port):
        GPIO.__init__(self, port)

    def start(self):
        logger.info('Starting GPIOLowLevel %s', self.path)
        self.__write_param__('value', '0')

    def stop(self):
        logger.info('Stopping GPIOLowLevel %s', self.path)
        self.__write_param__('value', '1')

    def destroy(self):
        logger.info('Destroying GPIOLowLevel %s', self.path)
