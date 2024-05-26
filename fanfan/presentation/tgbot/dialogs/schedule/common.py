from typing import Optional

from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.common import ManagedScroll

from fanfan.application.dto.user import FullUserDTO
from fanfan.application.exceptions.event import EventNotFound, NoCurrentEvent
from fanfan.application.holder import AppHolder
from fanfan.presentation.tgbot.dialogs.schedule.constants import (
    DATA_PAGE_BEFORE_SEARCH,
    DATA_SEARCH_QUERY,
    ID_SCHEDULE_SCROLL,
)


async def show_event_page(manager: DialogManager, event_id: int):
    user: FullUserDTO = manager.middleware_data["user"]
    app: AppHolder = manager.middleware_data["app"]
    try:
        page = await app.schedule.get_page_number_by_event(
            event_id=event_id,
            events_per_page=user.settings.items_per_page,
            search_query=manager.dialog_data.get(DATA_SEARCH_QUERY, None),
        )
        await manager.find(ID_SCHEDULE_SCROLL).set_page(page)
    except EventNotFound:
        pass


async def update_schedule(
    manager: DialogManager,
):
    app: AppHolder = manager.middleware_data["app"]
    try:
        current_event = await app.schedule.get_current_event()
        await show_event_page(manager, current_event.id)
    except NoCurrentEvent:
        await manager.find(ID_SCHEDULE_SCROLL).set_page(0)


async def set_search_query(
    dialog_manager: DialogManager,
    search_query: Optional[str],
):
    scroll: ManagedScroll = dialog_manager.find(ID_SCHEDULE_SCROLL)
    if search_query is None:
        await scroll.set_page(
            dialog_manager.dialog_data.get(DATA_PAGE_BEFORE_SEARCH, 0)
        )
    else:
        dialog_manager.dialog_data[DATA_PAGE_BEFORE_SEARCH] = await scroll.get_page()
        await scroll.set_page(0)
    dialog_manager.dialog_data[DATA_SEARCH_QUERY] = search_query
