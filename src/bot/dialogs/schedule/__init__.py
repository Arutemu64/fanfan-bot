from aiogram_dialog import Dialog

from src.bot.dialogs.schedule.tools.set_manual_event import set_manual_event_window
from src.bot.dialogs.schedule.tools.swap_events import swap_events_window
from src.bot.dialogs.schedule.tools.toggle_event_hidden import (
    toggle_event_hidden_window,
)

from .common import on_start_update_schedule
from .main import schedule_main_window
from .subscriptions import (
    event_selection_window,
    setup_subscription_window,
    subscriptions_window,
)

dialog = Dialog(
    schedule_main_window,
    set_manual_event_window,
    swap_events_window,
    toggle_event_hidden_window,
    event_selection_window,
    setup_subscription_window,
    subscriptions_window,
    on_start=on_start_update_schedule,
)