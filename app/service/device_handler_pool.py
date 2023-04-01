import logging

from app.models import Device
from app.system.devices import Device as DeviceHandler

logger = logging.getLogger(__name__)


class DeviceHandlerPool:
    def __init__(self):
        self.pool = dict[int, DeviceHandler]()

    def load_devices(self):
        for device in Device.all():
            logger.info('Loading device %s (%d)', device.name, device.id)
            handler = device.build_handler()
            if handler is None or device.id is None:
                logger.error('Cannot load device %s', device.name)
            else:
                self.pool[device.id] = handler

    def get_handler(self, device_id: int):
        return self.pool.get(device_id)

    def reset(self):
        logger.info('Destroying devices and resetting device pool')
        for device in self.pool.values():
            device.destroy()
        self.pool = {}
