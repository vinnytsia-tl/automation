import logging
from os import path

from . import Device

logger = logging.getLogger(__name__)


class GPIO(Device):
    INIT_PATH = '/sys/class/gpio/export'
    PORT_PATH = '/sys/class/gpio/gpio{}'

    def __init__(self, port):
        self.path = self.PORT_PATH.format(port)
        if not path.exists(self.path):
            self.__write_to_file__(self.INIT_PATH, str(port))
            self.__write_param__('direction', 'out')
        self.stop()
        logger.info('GPIO initialized for port %s', port)

    def __write_param__(self, param, value):
        self.__write_to_file__('{}/{}'.format(self.path, param), value)

    @staticmethod
    def __write_to_file__(filename, data):
        with open(filename, 'w') as file:
            file.write(data)
        logger.debug('Wrote %s to file %s', data, filename)
