from typing import TYPE_CHECKING

from aiogram_dialog import Dialog, DialogManager

from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.utils import merge_start_data

from .common import get_current_event, show_event_page
from .list_schedule import schedule_main_window
from .move_event import move_event_window
from .subscriptions.create_subscription import set_subscription_counter_window
from .subscriptions.list_subscriptions import subscriptions_main_window
from .view_event import selected_event_window

if TYPE_CHECKING:
    from aiogram.fsm.context import FSMContext


async def on_start_schedule(start_data: dict | None, manager: DialogManager) -> None:
    # Enable search
    state: FSMContext = manager.middleware_data["state"]
    await state.set_state(states.InlineQuerySearch.EVENTS)

    # Merge start data to dialog data
    await merge_start_data(start_data, manager)

    # Set page to current event
    if current_event := await get_current_event(manager):
        await show_event_page(manager, current_event.id)


schedule_dialog = Dialog(
    schedule_main_window,
    subscriptions_main_window,
    selected_event_window,
    move_event_window,
    set_subscription_counter_window,
    on_start=on_start_schedule,
)
