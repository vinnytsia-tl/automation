import asyncio
import logging
from typing import Any, Hashable, Optional, Protocol

logger = logging.getLogger(__name__)


class TimerHandle(Protocol):
    def cancel(self):
        ...

    def when(self) -> float:
        ...


class Device:
    stop_handles: dict[Any, TimerHandle] = {}

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}>'

    def parse_run_options(self, _run_options: Optional[str]) -> Any:
        return None

    def key(self, _run_options: Any) -> Hashable:
        return None

    def stop_delay(self, _run_options: Any) -> float:
        return 0

    def preload(self, run_options: Any):
        logger.info("Device %s preloading with options %s", repr(self), repr(run_options))

    def start(self, run_options: Any):
        logger.info('Starting %s with options %s', repr(self), repr(run_options))

    def stop(self, run_options: Any):
        logger.info('Stopping %s with options %s', repr(self), repr(run_options))
        self.stop_handles.pop(self.key(run_options), None)

    def destroy(self):
        logger.info('Destroying %s', repr(self))
        for stop_handle in self.stop_handles.values():
            stop_handle.cancel()

    def run(self, duration: int, run_options: Any):
        logger.info('Running %s for %d seconds', repr(self), duration)

        key = self.key(run_options)  # pylint: disable=assignment-from-none
        repr_key = f'{repr(self)} for {key}'

        event_loop = asyncio.get_event_loop()
        stop_time = event_loop.time() + duration - self.stop_delay(run_options)

        stop_handle = self.stop_handles.get(key, None)

        if stop_handle is None:
            logger.debug('%s not running, starting it at %d', repr_key, event_loop.time())
            event_loop.call_soon(self.start, run_options)
            logger.debug('Scheduling %s to stop at %d', repr_key, stop_time)
            self.stop_handles[key] = event_loop.call_at(stop_time, self.stop, run_options)
            return

        scheduled_stop_time = stop_handle.when()
        logger.debug('%s already running, skipping start. Scheduled stop time is %d', repr_key, scheduled_stop_time)

        if scheduled_stop_time < stop_time:
            logger.debug('Extending run time till %d', stop_time)
            stop_handle.cancel()
            self.stop_handles[key] = event_loop.call_at(stop_time, self.stop, run_options)
        else:
            logger.debug('Run time is already sufficient')
