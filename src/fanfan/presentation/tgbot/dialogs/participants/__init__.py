from typing import TYPE_CHECKING

from aiogram_dialog import Dialog, DialogManager

from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.participants.filter_nominations import (
    filter_nominations_window,
)
from fanfan.presentation.tgbot.dialogs.participants.list_participants import (
    list_participants_window,
)
from fanfan.presentation.tgbot.dialogs.participants.view_participant import (
    view_participant_window,
)

if TYPE_CHECKING:
    from aiogram.fsm.context import FSMContext


async def on_start_participants(
    start_data: dict | None, manager: DialogManager
) -> None:
    # Enable search
    state: FSMContext = manager.middleware_data["state"]
    await state.set_state(states.InlineQuerySearch.PARTICIPANTS)


dialog = Dialog(
    list_participants_window,
    view_participant_window,
    filter_nominations_window,
    on_start=on_start_participants,
)
