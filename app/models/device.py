from __future__ import annotations
from enum import Enum
from dataclasses import dataclass
from typing import List

from ..database import Database


class DeviceType(Enum):
    GPIO = 1
    MAX = 2


@dataclass
class Device:
    id: int
    name: str
    description: str
    type: DeviceType
    options: str

    def __init__(self, dev_id: int = None, name: str = None, description: str = None,
                 dev_type: DeviceType = None, options: str = None):
        self.id = dev_id
        self.name = name
        self.description = description
        self.type = dev_type
        self.options = options

    @staticmethod
    def create(db: Database, dev_id: int, name: str, description: str,
               dev_type: DeviceType, options: str) -> Device:

        cursor = db.cursor()
        cursor.execute('''
            INSERT INTO "devices" (
                "id", "name", "description", "type", "options"
            ) VALUES (?, ?, ?, ?, ?)
        ''', (
            dev_id, name, description, dev_type, options
        ))
        db.commit()
        return Device(dev_id, name, description, dev_type, options)

    def save(self, db: Database) -> Device:
        cursor = db.cursor()
        cursor.execute('''
            UPDATE "devices"
            SET "name" = ?,
                "description" = ?,
                "dev_type" = ?,
                "options" = ?
            WHERE "id" = ?
        ''', (
            self.name, self.description, self.type, self.options, self.id
        ))
        db.commit()
        return self

    @staticmethod
    def all(db: Database) -> List[Device]:
        cursor = db.cursor()
        cursor.execute('''
            SELECT "id", "name", "description", "type", "options"
            FROM "devices"
        ''')

        return [Device(*values) for values in cursor.fetchall()]
