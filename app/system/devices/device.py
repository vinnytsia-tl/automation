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
        logger.info('Running %s for %d seconds', repr(self), duration)

        event_loop = asyncio.get_event_loop()
        stop_time = event_loop.time() + duration - self.stop_delay

        if self.stop_handle is None:
            logger.debug('Device not running, starting it')
            event_loop.call_soon(self.start)
            logger.debug('Scheduling device to stop at %d', stop_time)
            self.stop_handle = event_loop.call_at(stop_time, self.stop)
            return

        scheduled_stop_time = self.stop_handle.when()
        logger.debug('Device already running, skipping start. Scheduled stop time is %d', scheduled_stop_time)

        if scheduled_stop_time < stop_time:
            logger.debug('Extending run time till %d', stop_time)
            self.stop_handle.cancel()
            self.stop_handle = event_loop.call_at(stop_time, self.stop)
        else:
            logger.debug('Run time is already sufficient')
