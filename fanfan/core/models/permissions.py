from __future__ import annotations

from dataclasses import dataclass


@dataclass(kw_only=True)
class UserPermissions:
    user_id: UserId

    can_send_feedback: bool = True
    can_edit_schedule: bool = False
    can_create_tickets: bool = False


from fanfan.core.models.user import UserId  # noqa: E402
