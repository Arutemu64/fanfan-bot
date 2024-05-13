from aiogram_dialog import Dialog, DialogManager

from fanfan.application.exceptions import ServiceError
from fanfan.application.holder import AppHolder

from .windows import (
    move_event_window,
    selected_event_window,
    set_subscription_counter_window,
)


async def on_start(start_data: int, manager: DialogManager):
    app: AppHolder = manager.middleware_data["app"]
    try:
        await app.schedule.get_event(start_data)
    except ServiceError:  # TODO Better error handling
        await manager.done()


dialog = Dialog(
    selected_event_window,
    move_event_window,
    set_subscription_counter_window,
    on_start=on_start,
)
