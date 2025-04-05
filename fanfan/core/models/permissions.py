from __future__ import annotations

from dataclasses import dataclass


@dataclass(kw_only=True)
class UserPermissions:
    user_id: UserId

    # Feedback
    can_send_feedback: bool

    # Helper specific
    helper_can_edit_schedule: bool


from fanfan.core.models.user import UserId  # noqa: E402
