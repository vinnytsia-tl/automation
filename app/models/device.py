from __future__ import annotations
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional

from app.config import Config


class DeviceType(Enum):
    GPIOLOWLEVEL = 1
    GPIOHIGHLEVEL = 2
    AUDIO = 3

    @staticmethod
    def cast(value: int | str | DeviceType | None) -> Optional[DeviceType]:
        if value is None:
            return None
        if isinstance(value, DeviceType):
            return value
        if isinstance(value, int):
            return DeviceType(value)
        if isinstance(value, str):
            return DeviceType[value]
        raise TypeError(f"Cannot cast {value} to DeviceType")


INSERT_SQL = 'INSERT INTO "devices" ("name", "description", "type", "options") VALUES (?, ?, ?, ?)'
UPDATE_SQL = 'UPDATE "devices" SET "name" = ?, "description" = ?, "type" = ?, "options" = ? WHERE "id" = ?'
FETCH_SQL = 'SELECT "id", "name", "description", "type", "options" FROM "devices"'


@dataclass
class Device:
    id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[DeviceType] = None
    options: Optional[str] = None

    def __post_init__(self):
        self.type = DeviceType.cast(self.type)

    def save(self):
        with Config.database.get_connection() as db:
            if self.id is None:
                cursor = db.execute(INSERT_SQL, (self.name, self.description, self.type.value, self.options))
                self.id = cursor.lastrowid
            else:
                db.execute(UPDATE_SQL, (self.name, self.description, self.type.value, self.options, self.id))

    def destroy(self):
        with Config.database.get_connection() as db:
            db.execute('DELETE FROM "devices" WHERE "id" = ?', (self.id,))

    @staticmethod
    def all() -> List[Device]:
        cursor = Config.database.execute(FETCH_SQL)
        return [Device(*values) for values in cursor.fetchall()]

    @staticmethod
    def find(device_id: int) -> Device:
        row = Config.database.execute(f'{FETCH_SQL} WHERE "id" = ?', (device_id,)).fetchone()
        if row is None:
            raise ValueError(f'Device with id {device_id} not found')
        return Device(*row)
