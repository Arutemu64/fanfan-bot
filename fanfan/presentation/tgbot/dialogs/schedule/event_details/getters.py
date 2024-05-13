from aiogram_dialog import DialogManager

from fanfan.application.dto.user import FullUserDTO
from fanfan.application.exceptions.event import EventNotFound
from fanfan.application.holder import AppHolder


async def selected_event_getter(
    dialog_manager: DialogManager,
    app: AppHolder,
    user: FullUserDTO,
    **kwargs,
):
    try:
        selected_event = await app.schedule.get_schedule_event(
            event_id=dialog_manager.start_data,
            user_id=user.id,
        )
    except EventNotFound:
        return
    return {
        "selected_event": selected_event,
    }
