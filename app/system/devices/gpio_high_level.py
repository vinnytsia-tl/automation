import logging
from typing import Any, Optional

from . import GPIO

logger = logging.getLogger(__name__)


class GPIOHighLevel(GPIO):
    def __init__(self, port: int):
        GPIO.__init__(self, port)

    def start(self, run_options: Optional[Any]):
        super().start(run_options)
        self.__write_param__('value', '1')

    def stop(self, run_options: Optional[Any]):
        super().stop(run_options)
        self.__write_param__('value', '0')
