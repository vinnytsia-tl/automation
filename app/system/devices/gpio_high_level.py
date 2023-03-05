import logging
from . import GPIO

logger = logging.getLogger(__name__)


class GPIOHighLevel(GPIO):
    def __init__(self, port):
        GPIO.__init__(self, port)

    def start(self):
        logger.info('Starting GPIOHighLevel %s', self.path)
        self.__write_param__('value', '1')

    def stop(self):
        logger.info('Stopping GPIOHighLevel %s', self.path)
        self.__write_param__('value', '0')

    def destroy(self):
        logger.info('Destroying GPIOHighLevel %s', self.path)
