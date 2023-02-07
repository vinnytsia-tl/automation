from __future__ import annotations
from enum import Enum
from dataclasses import dataclass
from typing import List

from ..database import Database


@dataclass
class Rule:
    id: int
    name: str
    description: str
    device_id: int
    start_time: int
    duration: int

    def __init__(self, rule_id: int = None, name: str = None, description: str = None,
                 device_id: int = None, start_time: int = None, duration: int = None):
        self.id = rule_id
        self.name = name
        self.description = description
        self.device_id = device_id
        self.start_time = start_time
        self.duration = duration

    @staticmethod
    def create(db: Database, rule_id: int = None, name: str = None, description: str = None,
                 device_id: int = None, start_time: int = None, duration: int = None) -> Rule:

        cursor = db.cursor()
        cursor.execute('''
            INSERT INTO "rules" (
                "id", "name", "description", "device_id", "start_time", "duration"
            ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            rule_id, name, description, device_id, start_time, duration
        ))
        db.commit()
        return Rule(rule_id, name, description, device_id, start_time, duration)

    @staticmethod
    def create2(db: Database, name: str = None, description: str = None,
                 device_id: int = None, start_time: int = None, duration: int = None) -> Rule:

        cursor = db.cursor()
        cursor.execute('''
            INSERT INTO "rules" (
                 "name", "description", "device_id", "start_time", "duration"
            ) VALUES (?, ?, ?, ?, ?)
        ''', (
            name, description, device_id, start_time, duration
        ))
        rule_id = db.commit()
        return Rule(rule_id, name, description, device_id, start_time, duration)

    def save(self, db: Database) -> Rule:
        cursor = db.cursor()
        cursor.execute('''
            UPDATE "rules"
            SET "name" = ?,
                "description" = ?,
                "device_id" = ?,
                "start_time" = ?
                "duration" = ?
            WHERE "id" = ?
        ''', (
            self.name, self.description, self.device_id, self.start_time, self.duration, self.id
        ))
        db.commit()
        return self

    @staticmethod
    def all(db: Database) -> List[Rule]:
        cursor = db.cursor()
        cursor.execute('''
            SELECT "id", "name", "description", "device_id", "start_time", "duration"
            FROM "rules"
        ''')

        return [Rule(*values) for values in cursor.fetchall()]
