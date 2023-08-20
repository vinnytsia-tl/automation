from __future__ import annotations

from dataclasses import dataclass
from enum import Flag, auto
from typing import Any, List, Optional

from app.config import Config
from app.models import Device

ATTRIBUTES = ["name", "description", "device_id", "start_time", "duration", "days_of_week", "run_options", "disabled"]
PREFIXED_ATTRIBUTES = [f'"rules"."{attr}"' for attr in ATTRIBUTES]
INSERT_SQL = f'INSERT INTO "rules" ({",".join(ATTRIBUTES)}) VALUES ({",".join(["?"] * len(ATTRIBUTES))})'
UPDATE_SQL = f'UPDATE "rules" SET {",".join([f"{attr} = ?" for attr in ATTRIBUTES])} WHERE "id" = ?'
FETCH_SQL = f'SELECT "rules"."id", {",".join(PREFIXED_ATTRIBUTES)} FROM "rules"'
FETCH_SQL_ENABLED = f'''
    {FETCH_SQL}
    INNER JOIN "devices" ON "rules"."device_id" = "devices"."id" AND "devices"."disabled" = 0
    WHERE "rules"."disabled" = 0
'''
FETCH_SQL_DEFAULT_ORDER = f'{FETCH_SQL} ORDER BY "rules"."disabled" ASC, "rules"."start_time" ASC'


class DayOfWeek(Flag):
    MONDAY = auto()
    TUESDAY = auto()
    WEDNESDAY = auto()
    THURSDAY = auto()
    FRIDAY = auto()
    SATURDAY = auto()
    SUNDAY = auto()

    @staticmethod
    def cast(value: int | str | DayOfWeek | None) -> Optional[DayOfWeek]:
        if value is None:
            return None
        if isinstance(value, DayOfWeek):
            return value
        if isinstance(value, int):
            return DayOfWeek(value)
        return DayOfWeek(int(value))

    def to_ukrainian(self):
        uk_names = {
            DayOfWeek.MONDAY: 'Понеділок',
            DayOfWeek.TUESDAY: 'Вівторок',
            DayOfWeek.WEDNESDAY: 'Середа',
            DayOfWeek.THURSDAY: 'Четвер',
            DayOfWeek.FRIDAY: 'П\'ятниця',
            DayOfWeek.SATURDAY: 'Субота',
            DayOfWeek.SUNDAY: 'Неділя'
        }

        names = [uk_names[day] for day in DayOfWeek if day in self]
        return ', '.join(names)


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
    days_of_week: Optional[DayOfWeek] = None
    run_options: Optional[str] = None
    disabled: bool = False

    def __post_init__(self):
        self.days_of_week = DayOfWeek.cast(self.days_of_week)
        self.disabled = bool(self.disabled)  # sqlite3 returns 0 or 1

    def __attribute_before_type_cast(self, attribute: str) -> Any:
        if attribute == 'days_of_week':
            return self.days_of_week.value if self.days_of_week is not None else None
        return getattr(self, attribute)

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

    def get_end_time(self) -> str | None:
        if self.start_time is None:
            return None
        if self.duration is None:
            return None
        return format_duration(self.start_time + self.duration)

    def save(self):
        with Config.database.get_connection() as db:
            attrs = [self.__attribute_before_type_cast(attr) for attr in ATTRIBUTES]
            if self.id is None:
                cursor = db.execute(INSERT_SQL, attrs)
                self.id = cursor.lastrowid
            else:
                db.execute(UPDATE_SQL, attrs + [self.id])

    def destroy(self):
        with Config.database.get_connection() as db:
            db.execute('DELETE FROM "rules" WHERE "id" = ?', (self.id,))

    @staticmethod
    def all() -> List[Rule]:
        cursor = Config.database.execute(FETCH_SQL_DEFAULT_ORDER)
        return [Rule(*values) for values in cursor.fetchall()]

    @staticmethod
    def enabled() -> List[Rule]:
        cursor = Config.database.execute(FETCH_SQL_ENABLED)
        return [Rule(*values) for values in cursor.fetchall()]

    @staticmethod
    def find(rule_id: int) -> Rule:
        row = Config.database.execute(f'{FETCH_SQL} WHERE "id" = ?', (rule_id,)).fetchone()
        if row is None:
            raise ValueError(f'Rule with id {rule_id} not found')
        return Rule(*row)
