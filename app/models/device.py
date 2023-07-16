from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, List, Optional

import yaml

from app.config import Config
from app.system.devices import Audio
from app.system.devices import Device as DeviceHandler
from app.system.devices import GPIOHighLevel, GPIOLowLevel


class DeviceType(Enum):
    GPIO_LOW_LEVEL = 1
    GPIO_HIGH_LEVEL = 2
    AUDIO = 3

    @staticmethod
    def cast(value: int | str | DeviceType | None) -> Optional[DeviceType]:
        if value is None:
            return None
        if isinstance(value, DeviceType):
            return value
        if isinstance(value, int):
            return DeviceType(value)
        return DeviceType[value]


ATTRIBUTES = ["name", "description", "type", "options", "disabled",
              "dependent_device_id", "dependent_start_delay", "dependent_stop_delay"]
INSERT_SQL = f'INSERT INTO "devices" ({",".join(ATTRIBUTES)}) VALUES ({",".join(["?"] * len(ATTRIBUTES))})'
UPDATE_SQL = f'UPDATE "devices" SET {",".join([f"{attr} = ?" for attr in ATTRIBUTES])} WHERE "id" = ?'
RULES_EXIST_SQL = 'EXISTS(SELECT 1 FROM "rules" WHERE "device_id" = "devices"."id")'
FETCH_SQL = f'SELECT "id", {",".join(ATTRIBUTES)}, {RULES_EXIST_SQL} FROM "devices"'


@dataclass
class Device:
    id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[DeviceType] = None
    options: Optional[str] = None
    disabled: bool = False
    dependent_device_id: Optional[int] = None
    dependent_start_delay: Optional[int] = None
    dependent_stop_delay: Optional[int] = None
    rules_exist: bool = False

    def __post_init__(self):
        self.type = DeviceType.cast(self.type)
        self.disabled = bool(self.disabled)  # sqlite3 returns 0 or 1
        self.rules_exist = bool(self.rules_exist)  # sqlite3 returns 0 or 1

    def __attribute_before_type_cast(self, attribute: str) -> Any:
        if attribute == 'type':
            return self.type.value if self.type is not None else None
        return getattr(self, attribute)

    def save(self):
        with Config.database.get_connection() as db:
            if self.id is None:
                cursor = db.execute(INSERT_SQL, [self.__attribute_before_type_cast(attr) for attr in ATTRIBUTES])
                self.id = cursor.lastrowid
            else:
                db.execute(UPDATE_SQL, [self.__attribute_before_type_cast(attr) for attr in ATTRIBUTES] + [self.id])

    def destroy(self):
        with Config.database.get_connection() as db:
            db.execute('DELETE FROM "devices" WHERE "id" = ?', (self.id,))

    def build_handler(self) -> DeviceHandler | None:
        if not self.options:
            return None
        options = yaml.safe_load(self.options)
        if self.type == DeviceType.GPIO_LOW_LEVEL:
            return GPIOLowLevel(**options)
        if self.type == DeviceType.GPIO_HIGH_LEVEL:
            return GPIOHighLevel(**options)
        if self.type == DeviceType.AUDIO:
            return Audio(**options)
        return None

    @staticmethod
    def all() -> List[Device]:
        cursor = Config.database.execute(f'{FETCH_SQL} ORDER BY "disabled" ASC, "name" ASC')
        return [Device(*values) for values in cursor.fetchall()]

    @staticmethod
    def enabled() -> List[Device]:
        cursor = Config.database.execute(f'{FETCH_SQL} WHERE "disabled" = 0')
        return [Device(*values) for values in cursor.fetchall()]

    @staticmethod
    def find(device_id: int) -> Device:
        row = Config.database.execute(f'{FETCH_SQL} WHERE "id" = ?', (device_id,)).fetchone()
        if row is None:
            raise ValueError(f'Device with id {device_id} not found')
        return Device(*row)
