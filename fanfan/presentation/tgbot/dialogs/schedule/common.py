from aiogram_dialog import DialogManager
from dishka import AsyncContainer

from fanfan.application.events.get_current_event import GetCurrentEvent
from fanfan.application.events.get_page_number_by_event import (
    GetPageNumberByEvent,
    GetPageNumberByEventDTO,
)
from fanfan.application.events.get_schedule_page import (
    GetSchedulePage,
    GetSchedulePageDTO,
)
from fanfan.core.dto.page import Pagination
from fanfan.core.exceptions.base import AppException
from fanfan.core.exceptions.schedule import NoCurrentEvent
from fanfan.core.models.event import EventId
from fanfan.core.models.user import UserFull
from fanfan.core.services.access import AccessService

ID_SCHEDULE_SCROLL = "schedule_scroll"
DATA_SELECTED_EVENT_ID = "selected_event_id"
DATA_TOTAL_PAGES = "total_pages"

CAN_EDIT_SCHEDULE = "can_edit_schedule"


async def schedule_getter(
    dialog_manager: DialogManager,
    container: AsyncContainer,
    user: UserFull,
    **kwargs,
):
    get_schedule_page: GetSchedulePage = await container.get(GetSchedulePage)

    page = await get_schedule_page(
        GetSchedulePageDTO(
            pagination=Pagination(
                limit=user.settings.items_per_page,
                offset=await dialog_manager.find(ID_SCHEDULE_SCROLL).get_page()
                * user.settings.items_per_page,
            )
        ),
    )
    dialog_manager.dialog_data[DATA_TOTAL_PAGES] = (
        page.total // user.settings.items_per_page
        + bool(page.total % user.settings.items_per_page)
    )

    return {
        "events": page.items,
        "page_number": await dialog_manager.find(ID_SCHEDULE_SCROLL).get_page() + 1,
        "pages": dialog_manager.dialog_data[DATA_TOTAL_PAGES],
    }


async def show_event_page(manager: DialogManager, event_id: EventId) -> None:
    container: AsyncContainer = manager.middleware_data["container"]
    get_page_number_by_event: GetPageNumberByEvent = await container.get(
        GetPageNumberByEvent
    )
    user: UserFull = manager.middleware_data["user"]

    page_number = await get_page_number_by_event(
        GetPageNumberByEventDTO(
            event_id=event_id, events_per_page=user.settings.items_per_page
        )
    )
    if page_number is not None:
        await manager.find(ID_SCHEDULE_SCROLL).set_page(page_number)


async def current_event_getter(
    container: AsyncContainer,
    **kwargs,
):
    get_current_event: GetCurrentEvent = await container.get(GetCurrentEvent)

    try:
        current_event = await get_current_event()
    except NoCurrentEvent:
        current_event = None

    return {
        "current_event": current_event,
    }


async def can_edit_schedule_getter(
    dialog_manager: DialogManager,
    container: AsyncContainer,
    user: UserFull,
    **kwargs,
):
    access: AccessService = await container.get(AccessService)

    try:
        await access.ensure_can_edit_schedule(user)
    except AppException:
        can_edit_schedule = False
    else:
        can_edit_schedule = True

    return {
        CAN_EDIT_SCHEDULE: can_edit_schedule,
    }
