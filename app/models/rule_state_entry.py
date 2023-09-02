from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from typing import Any, Optional

from pytz import UTC

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S %Z'


class RuleStatus(Enum):
    SCHEDULED = auto()
    RUNNING = auto()
    STOPPED = auto()


@dataclass
class RuleStateEntry:
    status: RuleStatus
    rule_name: Optional[str]
    device_name: Optional[str]
    run_options: Optional[str]
    recorded_start_time: Optional[float] = None
    recorded_stop_time: Optional[float] = None

    @property
    def status_css_class(self) -> str:
        if self.status == RuleStatus.SCHEDULED:
            return 'warning'
        if self.status == RuleStatus.RUNNING:
            return 'positive'
        if self.status == RuleStatus.STOPPED:
            return 'disabled'
        return ''

    @property
    def formatted_start_time(self) -> Optional[str]:
        if self.recorded_start_time is None:
            return None
        return datetime.fromtimestamp(self.recorded_start_time, UTC).strftime(DATETIME_FORMAT)

    @property
    def formatted_stop_time(self) -> Optional[str]:
        if self.recorded_stop_time is None:
            return None
        return datetime.fromtimestamp(self.recorded_stop_time, UTC).strftime(DATETIME_FORMAT)

    def as_json(self) -> dict[str, Any]:
        return {
            'status': self.status.name,
            'rule_name': self.rule_name,
            'device_name': self.device_name,
            'run_options': self.run_options,
            'recorded_start_time': self.recorded_start_time,
            'recorded_stop_time': self.recorded_stop_time
        }

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> RuleStateEntry:
        return cls(
            status=RuleStatus[data['status']],
            rule_name=data['rule_name'],
            device_name=data['device_name'],
            run_options=data['run_options'],
            recorded_start_time=data['recorded_start_time'],
            recorded_stop_time=data['recorded_stop_time']
        )
