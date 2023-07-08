from typing import Optional

from aiogram.filters.callback_data import CallbackData


class SendAnnouncementCallback(CallbackData, prefix="send_announcement"):
    current_event_id: Optional[int]
    next_event_id: Optional[int]


class ShowSchedule(CallbackData, prefix="schedule"):
    page: Optional[int]


class ShowNomination(CallbackData, prefix="nomination"):
    id: int


class ShowActivity(CallbackData, prefix="activity"):
    id: Optional[int]


class OpenMenu(CallbackData, prefix="open_menu"):
    menu: str
