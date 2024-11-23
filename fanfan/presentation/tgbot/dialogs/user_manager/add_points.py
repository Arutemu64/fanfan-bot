from typing import TYPE_CHECKING

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Counter, ManagedCounter, SwitchTo
from aiogram_dialog.widgets.text import Const

from fanfan.application.quest.add_points import AddPoints, AddPointsDTO
from fanfan.core.exceptions.users import TicketNotLinked
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.user_manager.common import DATA_USER_ID
from fanfan.presentation.tgbot.ui import strings

if TYPE_CHECKING:
    from dishka import AsyncContainer

ID_ADD_POINTS_COUNTER = "add_points_counter"


async def add_points_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    container: AsyncContainer = manager.middleware_data["container"]
    add_points: AddPoints = await container.get(AddPoints)
    counter: ManagedCounter = manager.find(ID_ADD_POINTS_COUNTER)

    try:
        await add_points(
            AddPointsDTO(
                user_id=manager.start_data[DATA_USER_ID],
                points=int(counter.get_value()),
            )
        )
        await manager.switch_to(states.UserManager.user_info)
    except TicketNotLinked:
        await callback.answer("⚠️ У участника не привязан билет", show_alert=True)


add_points_window = Window(
    Const("💰 Укажите, сколько очков добавить участнику"),
    Counter(
        id=ID_ADD_POINTS_COUNTER,
        plus=Const("➕"),
        minus=Const("➖"),
        min_value=1,
        max_value=5,
        default=1,
    ),
    Button(Const("✅ Добавить"), id="add_points", on_click=add_points_handler),
    SwitchTo(
        Const(strings.buttons.back), id="back", state=states.UserManager.user_info
    ),
    state=states.UserManager.add_points,
)
