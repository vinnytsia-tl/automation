import asyncio
import datetime
import logging
import signal
import time

from app.models import Rule

from .device_handler_pool import DeviceHandlerPool

SECONDS_IN_DAY = 24 * 60 * 60
logger = logging.getLogger(__name__)


class RuleScheduler:
    def __init__(self):
        self.device_handler_pool = DeviceHandlerPool()
        self.device_handler_pool.load_devices()
        self.event_loop = asyncio.get_event_loop()
        self.event_loop_offset = 0  # calculated during schedule

    def run_forever(self):
        self.__schedule_rules()
        self.__register_signal_handlers()
        self.event_loop.run_forever()

    def __schedule_rules(self):
        current_time = time.time()                     # wall clock time, utc
        event_loop_time = self.event_loop.time()       # monotonic time
        weekday_int = datetime.date.today().weekday()  # Monday is 0 and Sunday is 6
        weekday_mask = 1 << weekday_int                # Monday is 1 and Sunday is 64
        self.event_loop_offset = offset = event_loop_time - current_time
        midnight = datetime.datetime.combine(datetime.date.today(), datetime.time.min).timestamp()
        logger.info('Scheduling rules (current time: %d, event loop time: %d, '
                    'midnight: %d, offset: %d, weekday: %d, weekday mask: %d)',
                    current_time, event_loop_time, midnight, offset, weekday_int, weekday_mask)
        for rule in Rule.enabled():
            if rule.start_time is None or rule.days_of_week is None or rule.duration is None or rule.device_id is None:
                logger.warning('Skipping rule %s because it is not fully configured', rule.name or rule.id)
                continue
            start_time = midnight + rule.start_time
            stop_time = start_time + rule.duration
            if rule.days_of_week.value & weekday_mask != weekday_mask:
                logger.info('Skipping rule %s because today is not in its days of week', rule.name)
                continue
            if stop_time < current_time:
                logger.info('Skipping rule %s because its stop time is in the past', rule.name)
                continue
            logger.info('Scheduling rule %s at %d', rule.name, start_time)
            self.__schedule_device_run(rule.device_id, start_time + offset, rule.duration)
        logger.info('Scheduling next rule scheduling at %d', midnight + SECONDS_IN_DAY)
        self.event_loop.call_at(midnight + SECONDS_IN_DAY + offset, self.__schedule_rules)

    def __schedule_device_run(self, device_id: int, start_time: float, duration: int):
        logger.info('Scheduling device %d to run for %d at %d', device_id, duration, start_time - self.event_loop_offset)
        entry = self.device_handler_pool.get(device_id)
        if entry is None:
            logger.error('Cannot schedule device %d because it has no entry in the pool', device_id)
            return
        model, handler = entry
        self.event_loop.call_at(start_time, handler.run, duration)
        if model.dependent_device_id is not None:
            if model.dependent_start_delay is None or model.dependent_stop_delay is None:
                logger.error('Cannot schedule dependent device %d because it is not fully configured',
                             model.dependent_device_id)
                return
            self.__schedule_device_run(model.dependent_device_id, start_time - model.dependent_start_delay,
                                       duration + model.dependent_start_delay + model.dependent_stop_delay)

    def __cancel_scheduled_tasks(self):
        logger.info('Canceling scheduled tasks')
        for task in asyncio.all_tasks(loop=self.event_loop):
            if not task.done() and not task.cancelled():
                task.cancel()

    def __register_signal_handlers(self):
        self.event_loop.add_signal_handler(signal.SIGINT, self.__handle_stop_signal)
        self.event_loop.add_signal_handler(signal.SIGTERM, self.__handle_stop_signal)
        self.event_loop.add_signal_handler(signal.SIGHUP, self.__handle_restart_signal)

    def __handle_stop_signal(self):
        logger.info('Received a signal, shutting down...')
        self.event_loop.stop()
        self.__cancel_scheduled_tasks()
        self.device_handler_pool.reset()

    def __handle_restart_signal(self):
        logger.info('Received a signal, restarting...')
        self.__cancel_scheduled_tasks()
        self.device_handler_pool.reset()
        self.device_handler_pool.load_devices()
        self.__schedule_rules()
