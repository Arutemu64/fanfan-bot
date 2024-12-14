from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, kw_only=True)
class UserSettings:
    user_id: UserId
    items_per_page: int
    receive_all_announcements: bool

    # Org specific settings
    org_receive_feedback_notifications: bool


from fanfan.core.models.user import UserId  # noqa: E402
