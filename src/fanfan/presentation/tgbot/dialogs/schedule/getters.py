import math
import typing

from aiogram_dialog import DialogManager
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from fanfan.adapters.config.models import EnvConfig
from fanfan.core.constants.permissions import Permissions
from fanfan.core.dto.user import FullUserDTO
from fanfan.presentation.tgbot.dialogs.schedule.common import (
    ID_SCHEDULE_SCROLL,
    get_current_event,
    get_schedule,
)

if typing.TYPE_CHECKING:
    from aiogram_dialog.widgets.common import ManagedScroll


@inject
async def schedule_getter(
    dialog_manager: DialogManager,
    current_user: FullUserDTO,
    **kwargs,
):
    scroll: ManagedScroll = dialog_manager.find(ID_SCHEDULE_SCROLL)
    events = await get_schedule(dialog_manager)
    page = await scroll.get_page()
    per_page = current_user.settings.items_per_page

    start = page * per_page
    end = start + per_page

    return {
        "events": events[start:end],
        "page": await dialog_manager.find(ID_SCHEDULE_SCROLL).get_page() + 1,
        "pages": math.ceil(len(events) / per_page),
    }


async def current_event_getter(
    dialog_manager: DialogManager,
    **kwargs,
):
    current_event = await get_current_event(dialog_manager)
    return {
        "current_event": current_event,
        "current_event_queue": current_event.queue if current_event else None,
        "current_event_cumulative_duration": current_event.cumulative_duration
        if current_event
        else None,
    }


@inject
async def helpers_schedule_getter(
    dialog_manager: DialogManager,
    current_user: FullUserDTO,
    config: FromDishka[EnvConfig],
    **kwargs,
):
    return {
        Permissions.CAN_MANAGE_SCHEDULE: current_user.check_permission(
            Permissions.CAN_MANAGE_SCHEDULE
        ),
        "docs_link": config.docs_link,
    }
