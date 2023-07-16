import asyncio
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class Device:
    stop_handle: Optional[asyncio.TimerHandle] = None

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}>'

    def start(self) -> None:
        logger.info('Starting %s', repr(self))

    def stop(self, force: bool = False) -> None:
        logger.info('Stopping %s, force=%s', repr(self), force)
        self.stop_handle = None

    def destroy(self) -> None:
        logger.info('Destroying %s', repr(self))
        if self.stop_handle is not None:
            self.stop_handle.cancel()
            self.stop(True)

    @property
    def stop_delay(self) -> int:
        return 0

    def run(self, duration: int) -> None:
        event_loop = asyncio.get_event_loop()
        stop_time = event_loop.time() + duration - self.stop_delay

        if self.stop_handle is None:
            event_loop.call_soon(self.start)
            self.stop_handle = event_loop.call_at(stop_time, self.stop)
        elif self.stop_handle.when() < stop_time:
            self.stop_handle.cancel()
            self.stop_handle = event_loop.call_at(stop_time, self.stop)
