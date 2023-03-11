import asyncio
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
        self.active_rules = set[Rule]()

    def run_forever(self):
        self.__schedule_rules()
        self.__register_signal_handlers()
        self.event_loop.run_forever()

    def __schedule_rules(self):
        current_time = time.time()                # wall clock time
        event_loop_time = self.event_loop.time()  # monotonic time
        midnight = int(current_time) - (int(current_time) % SECONDS_IN_DAY)
        offset = event_loop_time - current_time
        logger.info('Scheduling rules (current time: %d, event loop time: %d, midnight: %d, offset: %d)',
                    current_time, event_loop_time, midnight, offset)
        for rule in Rule.all():
            start_time = midnight + rule.start_time
            stop_time = start_time + rule.duration
            if stop_time < current_time:
                logger.info('Skipping rule %s because its stop time is in the past', rule.name)
                continue
            logger.info('Scheduling rule %s at %d', rule.name, start_time)
            self.event_loop.call_at(start_time + offset, self.__start_rule, rule)
            self.event_loop.call_at(stop_time + offset, self.__stop_rule, rule)
        logger.info('Scheduling next rule scheduling at %d', midnight + SECONDS_IN_DAY)
        self.event_loop.call_at(midnight + SECONDS_IN_DAY + offset, self.__schedule_rules)

    def __cancel_scheduled_tasks(self):
        logger.info('Canceling scheduled tasks')
        for task in asyncio.all_tasks(loop=self.event_loop):
            if not task.done() and not task.cancelled():
                task.cancel()

    def __stop_active_rules(self):
        logger.info('Stopping active rules')
        for rule in self.active_rules:
            self.__stop_rule(rule)

    def __register_signal_handlers(self):
        self.event_loop.add_signal_handler(signal.SIGINT, self.__handle_stop_signal)
        self.event_loop.add_signal_handler(signal.SIGTERM, self.__handle_stop_signal)
        self.event_loop.add_signal_handler(signal.SIGHUP, self.__handle_restart_signal)

    def __handle_stop_signal(self, signum, _):
        logger.info('Received signal %d, shutting down...', signum)
        self.event_loop.stop()
        self.__cancel_scheduled_tasks()
        self.__stop_active_rules()
        self.device_handler_pool.reset()

    def __handle_restart_signal(self, signum, _):
        logger.info('Received signal %d, restarting...', signum)
        self.__cancel_scheduled_tasks()
        self.__stop_active_rules()
        self.device_handler_pool.reset()
        self.device_handler_pool.load_devices()
        self.__schedule_rules()

    def __start_rule(self, rule: Rule):
        logger.info('Starting rule %s', rule.name)
        handler = self.device_handler_pool.get_handler(rule.device_id)
        if handler is None:
            logger.error('No handler for device %d', rule.device_id)
        else:
            self.active_rules.add(rule)
            handler.start()

    def __stop_rule(self, rule: Rule):
        logger.info('Stopping rule %s', rule.name)
        handler = self.device_handler_pool.get_handler(rule.device_id)
        if handler is None:
            logger.error('No handler for device %d', rule.device_id)
        else:
            self.active_rules.remove(rule)
            handler.stop()
