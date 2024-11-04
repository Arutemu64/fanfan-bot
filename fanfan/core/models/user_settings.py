from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class UserSettingsModel:
    user_id: UserId
    items_per_page: int
    receive_all_announcements: bool


@dataclass(slots=True)
class OrgSettingsModel:
    user_id: UserId
    receive_feedback_notifications: bool


from fanfan.core.models.user import UserId  # noqa: E402
