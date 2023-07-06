from typing import Optional

from aiogram.filters.callback_data import CallbackData


class SendAnnouncementCallback(CallbackData, prefix="send_announcement"):
    current_event_id: Optional[int]
    next_event_id: Optional[int]
