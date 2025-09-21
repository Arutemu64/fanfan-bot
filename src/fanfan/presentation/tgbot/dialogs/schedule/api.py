from aiogram_dialog import DialogManager

from fanfan.core.vo.schedule_event import ScheduleEventId
from fanfan.presentation.tgbot import states


async def show_event_details(manager: DialogManager, event_id: ScheduleEventId) -> None:
    await manager.start(
        state=states.Schedule.EVENT_DETAILS, data={"event_id": event_id}
    )
