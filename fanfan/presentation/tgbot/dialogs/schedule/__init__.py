from typing import TYPE_CHECKING

from aiogram_dialog import Dialog, DialogManager

from fanfan.application.events.get_current_event import GetCurrentEvent
from fanfan.core.exceptions.schedule import NoCurrentEvent
from fanfan.presentation.tgbot import states

from .add_subscription import set_subscription_counter_window
from .common import show_event_page
from .event_details import selected_event_window
from .move_event import move_event_window
from .view_schedule import schedule_main_window
from .view_subscriptions import subscriptions_main_window

if TYPE_CHECKING:
    from aiogram.fsm.context import FSMContext
    from dishka import AsyncContainer


async def on_start_schedule(start_data: dict, manager: DialogManager) -> None:
    state: FSMContext = manager.middleware_data["state"]
    container: AsyncContainer = manager.middleware_data["container"]
    get_current_event = await container.get(GetCurrentEvent)

    # Enable search
    await state.set_state(states.InlineQuerySearch.EVENTS)

    try:
        current_event = await get_current_event()
        await show_event_page(manager, current_event.id)
    except NoCurrentEvent:
        pass


dialog = Dialog(
    schedule_main_window,
    subscriptions_main_window,
    selected_event_window,
    move_event_window,
    set_subscription_counter_window,
    on_start=on_start_schedule,
)
