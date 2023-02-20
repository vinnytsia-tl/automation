from os import path
from . import GPIO


class GPIOLowLevel(GPIO):
    def __init__(self, port):
        GPIO.__init__(self, port)

    def start(self):
        self.__write_param__('value', '0')

    def stop(self):
        self.__write_param__('value', '1')
