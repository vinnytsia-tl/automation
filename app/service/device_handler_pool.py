import logging
from typing import Optional

from app.models import Device as DeviceModel
from app.system.devices import Device as DeviceHandler

logger = logging.getLogger(__name__)


class DeviceHandlerPool:
    def __init__(self):
        self.pool = dict[int, tuple[DeviceModel, DeviceHandler]]()
        DeviceHandlerPool.instance = self

    def load_devices(self):
        for model in DeviceModel.enabled():
            logger.info('Loading device %s (%d)', model.name, model.id)
            if model.id is None:
                logger.error('Device %s does not have an ID', model.name)
                continue
            handler = model.build_handler()
            if handler is None:
                logger.error('Cannot build handler for device %s', model.name)
                continue
            self.pool[model.id] = (model, handler)

    def get(self, device_id: int) -> Optional[tuple[DeviceModel, DeviceHandler]]:
        return self.pool.get(device_id)

    def reset(self):
        logger.info('Destroying devices and resetting device pool')
        for (_model, handler) in self.pool.values():
            handler.destroy()
        self.pool = {}
