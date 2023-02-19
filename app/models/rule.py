from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional

from app.config import Config

INSERT_SQL = 'INSERT INTO "rules" ("name", "description", "device_id", "start_time", "duration") VALUES (?, ?, ?, ?, ?, ?)'
UPDATE_SQL = '''
    UPDATE "rules"
    SET "name" = ?,
        "description" = ?,
        "device_id" = ?,
        "start_time" = ?
        "duration" = ?
    WHERE "id" = ?
'''
FETCH_ALL_SQL = 'SELECT "id", "name", "description", "device_id", "start_time", "duration" FROM "rules"'


@dataclass
class Rule:
    id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    device_id: Optional[int] = None
    start_time: Optional[int] = None
    duration: Optional[int] = None

    def save(self):
        with Config.database.get_connection() as db:
            if self.id is None:
                cursor = db.execute(INSERT_SQL, (self.name, self.description,
                                    self.device_id, self.start_time, self.duration))
                self.id = cursor.lastrowid
            else:
                db.execute(UPDATE_SQL, (self.name, self.description,
                                        self.device_id, self.start_time, self.duration, self.id))

    @staticmethod
    def all() -> List[Rule]:
        cursor = Config.database.execute(FETCH_ALL_SQL)
        return [Rule(*values) for values in cursor.fetchall()]
