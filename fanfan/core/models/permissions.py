from __future__ import annotations

from dataclasses import dataclass


@dataclass(kw_only=True)
class UserPermissions:
    user_id: UserId

    can_send_feedback: bool
    can_edit_schedule: bool
    can_create_tickets: bool


from fanfan.core.models.user import UserId  # noqa: E402
