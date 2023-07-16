import logging
from os import path

from . import Device

logger = logging.getLogger(__name__)


class GPIO(Device):
    INIT_PATH = '/sys/class/gpio/export'
    PORT_PATH = '/sys/class/gpio/gpio{}'

    def __init__(self, port: int):
        self.path = self.PORT_PATH.format(port)
        if not path.exists(self.path):
            self.__write_to_file__(self.INIT_PATH, str(port))
            self.__write_param__('direction', 'out')
        self.stop()
        logger.info('GPIO initialized for port %s', port)

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} {self.path}>'

    def __write_param__(self, param: str, value: str):
        self.__write_to_file__(f'{self.path}/{param}', value)

    @staticmethod
    def __write_to_file__(filename: str, data: str):
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(data)
        logger.debug('Wrote %s to file %s', data, filename)
