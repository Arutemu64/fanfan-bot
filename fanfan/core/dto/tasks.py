from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True, frozen=True)
class TaskStatus:
    running: bool
    last_execution: datetime | None
