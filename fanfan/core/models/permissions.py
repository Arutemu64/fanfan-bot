from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class UserPermissionsModel:
    user_id: UserId
    can_send_feedback: bool


from fanfan.core.models.user import UserId  # noqa: E402
