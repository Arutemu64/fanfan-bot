import enum
from dataclasses import dataclass


class PermissionsList(enum.StrEnum):
    can_send_feedback = enum.auto()
    can_edit_schedule = enum.auto()
    can_create_tickets = enum.auto()


@dataclass(slots=True, kw_only=True)
class Permission:
    id: int | None = None
    name: PermissionsList
