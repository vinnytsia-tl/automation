from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from app.config import Config
from app.models import Device

INSERT_SQL = 'INSERT INTO "rules" ("name", "description", "device_id", "start_time", "duration") VALUES (?, ?, ?, ?, ?)'
UPDATE_SQL = '''
    UPDATE "rules"
    SET "name" = ?,
        "description" = ?,
        "device_id" = ?,
        "start_time" = ?,
        "duration" = ?
    WHERE "id" = ?
'''
FETCH_SQL = 'SELECT "id", "name", "description", "device_id", "start_time", "duration" FROM "rules"'


def parse_duration(duration: str) -> int:
    hours, minutes, seconds = duration.split(':')
    return int(hours) * 3600 + int(minutes) * 60 + int(seconds)


def format_duration(duration: int) -> str:
    hours = duration // 3600
    minutes = (duration % 3600) // 60
    seconds = duration % 60
    return f'{hours:02d}:{minutes:02d}:{seconds:02d}'


@dataclass
class Rule:
    id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    device_id: Optional[int] = None
    start_time: Optional[int] = None
    duration: Optional[int] = None

    def get_device(self) -> Device | None:
        if self.device_id is None:
            return None
        return Device.find(self.device_id)

    def get_start_time(self) -> str | None:
        if self.start_time is None:
            return None
        return format_duration(self.start_time)

    def get_duration(self) -> str | None:
        if self.duration is None:
            return None
        return format_duration(self.duration)

    def save(self):
        with Config.database.get_connection() as db:
            if self.id is None:
                cursor = db.execute(INSERT_SQL, (self.name, self.description,
                                    self.device_id, self.start_time, self.duration))
                self.id = cursor.lastrowid
            else:
                db.execute(UPDATE_SQL, (self.name, self.description,
                                        self.device_id, self.start_time, self.duration, self.id))

    def destroy(self):
        with Config.database.get_connection() as db:
            db.execute('DELETE FROM "rules" WHERE "id" = ?', (self.id,))

    @staticmethod
    def all() -> List[Rule]:
        cursor = Config.database.execute(FETCH_SQL)
        return [Rule(*values) for values in cursor.fetchall()]

    @staticmethod
    def find(rule_id: int) -> Rule:
        row = Config.database.execute(f'{FETCH_SQL} WHERE "id" = ?', (rule_id,)).fetchone()
        if row is None:
            raise ValueError(f'Rule with id {rule_id} not found')
        return Rule(*row)
