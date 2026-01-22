import typing

from aiogram_dialog import DialogManager

from fanfan.application.schedule.list_schedule import (
    ListSchedule,
    ListScheduleDTO,
)
from fanfan.core.dto.schedule import ScheduleEventDTO, UserScheduleEventDTO
from fanfan.core.dto.user import FullUserDTO
from fanfan.core.models.user import User
from fanfan.core.vo.schedule_event import ScheduleEventId, ScheduleEventPublicId
from fanfan.presentation.tgbot.dialogs.common.utils import (
    get_container,
    get_current_user,
)

if typing.TYPE_CHECKING:
    from aiogram_dialog.widgets.common import ManagedScroll

ID_SCHEDULE_SCROLL = "schedule_scroll"


async def get_schedule(
    dialog_manager: DialogManager, only_subscribed: bool = False
) -> list[UserScheduleEventDTO]:
    container = get_container(dialog_manager)
    get_schedule_page = await container.get(ListSchedule)
    page = await get_schedule_page(
        ListScheduleDTO(
            pagination=None,
            search_query=None,
            only_subscribed=only_subscribed,
        )
    )
    return page.items


async def get_current_event(manager: DialogManager) -> ScheduleEventDTO | None:
    events = await get_schedule(manager)
    return next((x for x in events if x.is_current), None)


async def show_event_page(manager: DialogManager, event_id: ScheduleEventId) -> None:
    current_user: FullUserDTO = get_current_user(manager)
    events = await get_schedule(manager)
    page = None
    for idx, event in enumerate(events):
        if event.id == event_id:
            page = idx // current_user.settings.items_per_page
    if page is not None:
        await manager.find(ID_SCHEDULE_SCROLL).set_page(page)


async def handle_schedule_text_input(
    dialog_manager: DialogManager, user_input: str, change_page: bool = True
) -> ScheduleEventDTO | None:
    schedule_scroll: ManagedScroll = dialog_manager.find(ID_SCHEDULE_SCROLL)
    events = await get_schedule(dialog_manager)
    if "/" in user_input and user_input.replace("/", "").isnumeric():
        # User clicked on public ID
        public_id = ScheduleEventPublicId(int(user_input.replace("/", "")))
        return next((x for x in events if x.public_id == public_id), None)
    if user_input.isnumeric():
        # User typed number so assume its page number
        current_user: User = dialog_manager.middleware_data["current_user"]
        total_pages = len(events) // current_user.settings.items_per_page + bool(
            len(events) % current_user.settings.items_per_page
        )
        if 1 <= int(user_input) <= total_pages:
            await schedule_scroll.set_page(int(user_input) - 1)
        return None
    return None
