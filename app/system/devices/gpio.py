from os import path
from . import Device


class GPIO(Device):
    INIT_PATH = '/sys/class/gpio/export'
    PORT_PATH = '/sys/class/gpio/gpio{}'

    def __init__(self, port):
        self.path = self.PORT_PATH.format(port)
        if not path.exists(self.path):
            self.__write_to_file__(self.INIT_PATH, str(port))
            self.__write_param__('direction', 'out')

    def start(self):
        self.__write_param__('value', '1')

    def stop(self):
        self.__write_param__('value', '0')

    def __write_param__(self, param, value):
        self.__write_to_file__('{}/{}'.format(self.path, param), value)

    @staticmethod
    def __write_to_file__(filename, data):
        with open(filename, 'w') as file:
            file.write(data)
