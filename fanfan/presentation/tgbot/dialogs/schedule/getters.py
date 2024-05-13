from aiogram_dialog import DialogManager

from fanfan.application.dto.user import FullUserDTO
from fanfan.application.exceptions.event import NoCurrentEvent
from fanfan.application.holder import AppHolder
from fanfan.common.enums import UserRole

from .constants import (
    DATA_SEARCH_QUERY,
    ID_SCHEDULE_SCROLL,
    ID_SUBSCRIPTIONS_SCROLL,
)


async def schedule_getter(
    dialog_manager: DialogManager,
    app: AppHolder,
    user: FullUserDTO,
    **kwargs,
):
    page = await app.schedule.get_schedule_page(
        page_number=await dialog_manager.find(ID_SCHEDULE_SCROLL).get_page(),
        events_per_page=user.settings.items_per_page,
        search_query=dialog_manager.dialog_data.get(DATA_SEARCH_QUERY, None),
        user_id=dialog_manager.event.from_user.id,
    )
    return {
        "events": page.items,
        "page_number": page.number + 1,
        "pages": page.total_pages,
        "is_helper": user.role
        in [UserRole.HELPER, UserRole.ORG],  # Move into common getter
    }


async def subscriptions_getter(
    dialog_manager: DialogManager,
    user: FullUserDTO,
    app: AppHolder,
    **kwargs,
):
    page = await app.subscriptions.get_subscriptions_page(
        page_number=await dialog_manager.find(ID_SUBSCRIPTIONS_SCROLL).get_page(),
        subscriptions_per_page=user.settings.items_per_page,
        user_id=user.id,
    )
    return {
        "subscriptions": page.items,
        "pages": page.total_pages,
    }


async def current_event_getter(
    app: AppHolder,
    **kwargs,
):
    try:
        current_event = await app.schedule.get_current_event()
    except NoCurrentEvent:
        current_event = None
    return {
        "current_event": current_event,
    }
