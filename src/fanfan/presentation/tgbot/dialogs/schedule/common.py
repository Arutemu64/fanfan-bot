from aiogram_dialog import DialogManager
from dishka import AsyncContainer

from fanfan.application.schedule.get_page_number_by_event import (
    GetPageNumberByEventDTO,
    GetPageNumberByScheduleEvent,
)
from fanfan.application.schedule.read_current_event import ReadCurrentScheduleEvent
from fanfan.application.schedule.read_schedule_page_for_user import (
    GetSchedulePageDTO,
    ReadSchedulePageForUser,
)
from fanfan.core.dto.page import Pagination
from fanfan.core.exceptions.base import AccessDenied
from fanfan.core.models.user import UserData
from fanfan.core.services.schedule import ScheduleService
from fanfan.core.vo.schedule_event import ScheduleEventId

ID_SCHEDULE_SCROLL = "schedule_scroll"
DATA_SELECTED_EVENT_ID = "selected_event_id"
DATA_TOTAL_PAGES = "total_pages"

CAN_EDIT_SCHEDULE = "can_edit_schedule"


async def schedule_getter(
    dialog_manager: DialogManager,
    container: AsyncContainer,
    user: UserData,
    **kwargs,
):
    get_schedule_page: ReadSchedulePageForUser = await container.get(
        ReadSchedulePageForUser
    )

    page = await get_schedule_page(
        GetSchedulePageDTO(
            pagination=Pagination(
                limit=user.settings.items_per_page,
                offset=await dialog_manager.find(ID_SCHEDULE_SCROLL).get_page()
                * user.settings.items_per_page,
            )
        ),
    )
    pages = page.total // user.settings.items_per_page + bool(
        page.total % user.settings.items_per_page
    )
    dialog_manager.dialog_data[DATA_TOTAL_PAGES] = pages

    return {
        "events": page.items,
        "page_number": await dialog_manager.find(ID_SCHEDULE_SCROLL).get_page() + 1,
        "pages": pages or 1,
    }


async def show_event_page(manager: DialogManager, event_id: ScheduleEventId) -> None:
    container: AsyncContainer = manager.middleware_data["container"]
    get_page_number_by_event: GetPageNumberByScheduleEvent = await container.get(
        GetPageNumberByScheduleEvent
    )
    user: UserData = manager.middleware_data["user"]

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
    get_current_event: ReadCurrentScheduleEvent = await container.get(
        ReadCurrentScheduleEvent
    )
    current_event = await get_current_event()

    return {
        "current_event_queue": current_event.queue if current_event else None,
        "current_event_cumulative_duration": current_event.cumulative_duration
        if current_event
        else None,
    }


async def can_edit_schedule_getter(
    dialog_manager: DialogManager,
    container: AsyncContainer,
    user: UserData,
    **kwargs,
):
    schedule_service: ScheduleService = await container.get(ScheduleService)

    try:
        schedule_service.ensure_user_can_manage_schedule(user)
    except AccessDenied:
        can_edit_schedule = False
    else:
        can_edit_schedule = True

    return {
        CAN_EDIT_SCHEDULE: can_edit_schedule,
    }
