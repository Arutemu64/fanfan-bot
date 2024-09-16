from aiogram_dialog import DialogManager
from dishka import AsyncContainer

from fanfan.application.events.get_current_event import GetCurrentEvent
from fanfan.application.events.get_page_number_by_event import GetPageNumberByEvent
from fanfan.application.events.get_schedule_page import GetSchedulePage
from fanfan.core.exceptions.events import NoCurrentEvent
from fanfan.core.models.page import Pagination
from fanfan.core.models.user import FullUserDTO

ID_SCHEDULE_SCROLL = "schedule_scroll"
DATA_SELECTED_EVENT_ID = "selected_event_id"
DATA_TOTAL_PAGES = "total_pages"


async def schedule_getter(
    dialog_manager: DialogManager,
    container: AsyncContainer,
    user: FullUserDTO,
    **kwargs,
):
    get_schedule_page = await container.get(GetSchedulePage)

    page = await get_schedule_page(
        pagination=Pagination(
            limit=user.settings.items_per_page,
            offset=await dialog_manager.find(ID_SCHEDULE_SCROLL).get_page()
            * user.settings.items_per_page,
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


async def show_event_page(manager: DialogManager, event_id: int) -> None:
    container: AsyncContainer = manager.middleware_data["container"]
    get_page_number_by_event = await container.get(GetPageNumberByEvent)
    user: FullUserDTO = manager.middleware_data["user"]

    page_number = await get_page_number_by_event(
        event_id=event_id,
        events_per_page=user.settings.items_per_page,
    )
    if page_number is not None:
        await manager.find(ID_SCHEDULE_SCROLL).set_page(page_number)


async def current_event_getter(
    container: AsyncContainer,
    **kwargs,
):
    get_current_event = await container.get(GetCurrentEvent)

    try:
        current_event = await get_current_event()
    except NoCurrentEvent:
        current_event = None

    return {
        "current_event": current_event,
    }
