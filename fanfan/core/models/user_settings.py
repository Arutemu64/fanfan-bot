from __future__ import annotations

from dataclasses import dataclass


@dataclass(kw_only=True)
class UserSettings:
    items_per_page: int = 5
    receive_all_announcements: bool = True

    # Org specific settings
    org_receive_feedback_notifications: bool = True
