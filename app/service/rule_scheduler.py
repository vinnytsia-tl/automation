import asyncio
import datetime
import logging
import signal
import time
from typing import Tuple

from app.models import Rule

from .device_handler_pool import DeviceHandlerPool

SECONDS_IN_DAY = 24 * 60 * 60
logger = logging.getLogger(__name__)


class RuleScheduler:
    def __init__(self):
        self.device_handler_pool = DeviceHandlerPool()
        self.device_handler_pool.load_devices()
        self.event_loop = asyncio.get_event_loop()
        self.active_rules = set[Tuple[str, int]]()

    def run_forever(self):
        self.__schedule_rules()
        self.__register_signal_handlers()
        self.event_loop.run_forever()

    def __schedule_rules(self):
        current_time = time.time()                     # wall clock time, utc
        event_loop_time = self.event_loop.time()       # monotonic time
        weekday_int = datetime.date.today().weekday()  # Monday is 0 and Sunday is 6
        weekday_mask = 1 << weekday_int                # Monday is 1 and Sunday is 64
        offset = event_loop_time - current_time
        midnight = datetime.datetime.combine(datetime.date.today(), datetime.time.min).timestamp()
        logger.info('Scheduling rules (current time: %d, event loop time: %d, '
                    'midnight: %d, offset: %d, weekday: %d, weekday mask: %d)',
                    current_time, event_loop_time, midnight, offset, weekday_int, weekday_mask)
        for rule in Rule.all():
            start_time = midnight + rule.start_time
            stop_time = start_time + rule.duration
            if rule.days_of_week & weekday_mask != weekday_mask:
                logger.info('Skipping rule %s because today is not in its days of week', rule.name)
                continue
            if stop_time < current_time:
                logger.info('Skipping rule %s because its stop time is in the past', rule.name)
                continue
            logger.info('Scheduling rule %s at %d', rule.name, start_time)
            self.event_loop.call_at(start_time + offset, self.__start_rule, rule.name, rule.device_id)
            self.event_loop.call_at(stop_time + offset, self.__stop_rule, rule.name, rule.device_id)
        logger.info('Scheduling next rule scheduling at %d', midnight + SECONDS_IN_DAY)
        self.event_loop.call_at(midnight + SECONDS_IN_DAY + offset, self.__schedule_rules)

    def __cancel_scheduled_tasks(self):
        logger.info('Canceling scheduled tasks')
        for task in asyncio.all_tasks(loop=self.event_loop):
            if not task.done() and not task.cancelled():
                task.cancel()

    def __stop_active_rules(self):
        logger.info('Stopping active rules')
        for (rule_name, device_id) in self.active_rules:
            self.__stop_rule(rule_name, device_id)

    def __register_signal_handlers(self):
        self.event_loop.add_signal_handler(signal.SIGINT, self.__handle_stop_signal)
        self.event_loop.add_signal_handler(signal.SIGTERM, self.__handle_stop_signal)
        self.event_loop.add_signal_handler(signal.SIGHUP, self.__handle_restart_signal)

    def __handle_stop_signal(self):
        logger.info('Received a signal, shutting down...')
        self.event_loop.stop()
        self.__cancel_scheduled_tasks()
        self.__stop_active_rules()
        self.device_handler_pool.reset()

    def __handle_restart_signal(self):
        logger.info('Received a signal, restarting...')
        self.__cancel_scheduled_tasks()
        self.__stop_active_rules()
        self.device_handler_pool.reset()
        self.device_handler_pool.load_devices()
        self.__schedule_rules()

    def __start_rule(self, rule_name: str, device_id: int):
        logger.info('Starting rule %s', rule_name)
        handler = self.device_handler_pool.get_handler(device_id)
        if handler is None:
            logger.error('No handler for device %d', device_id)
        else:
            self.active_rules.add((rule_name, device_id))
            handler.start()

    def __stop_rule(self, rule_name: str, device_id: int):
        logger.info('Stopping rule %s', rule_name)
        handler = self.device_handler_pool.get_handler(device_id)
        if handler is None:
            logger.error('No handler for device %d', device_id)
        else:
            self.active_rules.remove((rule_name, device_id))
            handler.stop()
