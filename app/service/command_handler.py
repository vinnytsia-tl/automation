import asyncio
import json
import logging
from math import inf as infinity
from typing import Optional

from .device_handler_pool import DeviceHandlerPool

logger = logging.getLogger(__name__)


class InfiniteStopHandle:
    def cancel(self):
        pass

    def when(self):
        return infinity


class CommandHandler(asyncio.Protocol):
    transport: Optional[asyncio.Transport] = None

    def __init__(self, device_handler_pool: DeviceHandlerPool):
        self.device_handler_pool = device_handler_pool

    def connection_made(self, transport: asyncio.BaseTransport):
        logger.debug('Received a new connection')
        assert isinstance(transport, asyncio.Transport)
        self.transport = transport

    def data_received(self, data: bytes):
        assert self.transport is not None

        logger.debug('Received data %s', repr(data))
        command = json.loads(data.decode())
        action: str = command['action']
        device_id: int = command['device_id']
        run_options: Optional[str] = command['run_options']

        try:
            if action == 'device_start':
                self.__device_start(device_id, run_options)
            elif action == 'device_stop':
                self.__device_stop(device_id, run_options)
            else:
                raise ValueError(f'Unknown action {command}')
        except Exception as err:  # pylint: disable=broad-except
            logger.error(repr(err))
            self.transport.write(json.dumps({'error': repr(err)}).encode())
        else:
            self.transport.write(json.dumps({'success': True}).encode())

    def __fetch_device(self, device_id: int, run_options: Optional[str]):
        entry = self.device_handler_pool.get(device_id)
        if entry is None:
            message = f'Cannot use device {device_id} because it has no entry in the pool'
            raise ValueError(message)

        model, handler = entry
        opts = handler.parse_run_options(run_options)
        handler.preload(opts)
        device_key = handler.key(opts)
        stop_handle = handler.stop_handles.pop(device_key, None)

        return model, handler, opts, device_key, stop_handle

    def __device_start(self, device_id: int, run_options: Optional[str]):
        logger.info('Executing the device start command device_id=%d run_options=%s', device_id, run_options)

        _, handler, opts, device_key, stop_handle = self.__fetch_device(device_id, run_options)

        if stop_handle is not None:
            logger.warning('Device %d is already running', device_id)
            logger.debug('Canceling scheduled stop for device %s', device_id)
            stop_handle.cancel()

        logger.debug('Disabling future auto-stop for device %d', device_id)
        handler.stop_handles[device_key] = InfiniteStopHandle()

        logger.debug('Starting device %d', device_id)
        handler.start(opts)

    def __device_stop(self, device_id: int, run_options: Optional[str]):
        logger.info('Executing the device stop command device_id=%d run_options=%s', device_id, run_options)

        _, handler, opts, _, stop_handle = self.__fetch_device(device_id, run_options)

        if stop_handle is None:
            logger.warning('Device %d is not running', device_id)
        else:
            logger.debug('Canceling scheduled stop for device %s', device_id)
            stop_handle.cancel()

        logger.debug('Stopping device %d', device_id)
        handler.stop(opts)
