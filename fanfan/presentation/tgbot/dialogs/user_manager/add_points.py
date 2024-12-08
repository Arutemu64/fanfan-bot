from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.input import ManagedTextInput, TextInput
from aiogram_dialog.widgets.kbd import Button, SwitchTo
from aiogram_dialog.widgets.text import Const, Jinja
from dishka import AsyncContainer

from fanfan.application.quest.add_points import AddPoints, AddPointsDTO
from fanfan.core.exceptions.users import TicketNotLinked
from fanfan.core.utils.pluralize import POINTS_PLURALS, pluralize
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.user_manager.common import (
    DATA_USER_ID,
    managed_user_getter,
)
from fanfan.presentation.tgbot.ui import strings

MAX_POINTS = 30

COMMENT = "comment"
POINTS = "points"


async def preview_add_points_getter(
    dialog_manager: DialogManager,
    container: AsyncContainer,
    **kwargs,
):
    points = int(dialog_manager.dialog_data[POINTS])
    return {
        "points": int(dialog_manager.dialog_data[POINTS]),
        "points_pluralized": pluralize(points, POINTS_PLURALS),
        "comment": dialog_manager.dialog_data[COMMENT],
    }


async def set_points_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: int,
) -> None:
    if 0 < data <= MAX_POINTS:
        dialog_manager.dialog_data[POINTS] = data
        await dialog_manager.switch_to(states.UserManager.set_comment)
        return
    await message.answer(f"⚠️ Количество очков должно быть от 0 до {MAX_POINTS}")


async def set_comment_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: str,
) -> None:
    dialog_manager.dialog_data[COMMENT] = data
    await dialog_manager.switch_to(states.UserManager.preview_add_points)


async def add_points_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    container: AsyncContainer = manager.middleware_data["container"]
    add_points: AddPoints = await container.get(AddPoints)

    try:
        await add_points(
            AddPointsDTO(
                user_id=manager.start_data[DATA_USER_ID],
                points=int(manager.dialog_data[POINTS]),
                comment=manager.dialog_data[COMMENT],
            )
        )
        await callback.answer("✅ Успешно")
        await manager.switch_to(states.UserManager.user_info)
    except TicketNotLinked:
        await callback.answer("⚠️ У участника не привязан билет", show_alert=True)


set_points_window = Window(
    Const(
        f"💰 Отправьте количество очков, "
        f"которое получит участник (от 0 до {MAX_POINTS})"
    ),
    TextInput(
        id="id_set_points_input",
        type_factory=int,
        on_success=set_points_handler,
    ),
    SwitchTo(
        Const(strings.buttons.back),
        id="back",
        state=states.UserManager.user_info,
    ),
    state=states.UserManager.set_points,
)

set_comment_window = Window(
    Const("💬 Теперь отправьте комментарий, который увидит участник"),
    TextInput(
        id="id_set_comment_input",
        type_factory=str,
        on_success=set_comment_handler,
    ),
    SwitchTo(
        Const(strings.buttons.back),
        id="back",
        state=states.UserManager.set_points,
    ),
    state=states.UserManager.set_comment,
)


preview_add_points_window = Window(
    Const("Давай всё проверим..."),
    Const(" "),
    Jinja(
        "💰 <b>{{ managed_user.username|e }}</b> "
        "получит <b>{{ points }} {{ points_pluralized }}</b>"
    ),
    Const(" "),
    Const("💬 Комментарий:"),
    Jinja("<blockquote>{{ comment }}</blockquote>"),
    Const(" "),
    Const("Всё хорошо?"),
    Button(
        Const("✅ Да"),
        id="add_points",
        on_click=add_points_handler,
    ),
    SwitchTo(
        Const(strings.buttons.back), id="back", state=states.UserManager.set_comment
    ),
    getter=[preview_add_points_getter, managed_user_getter],
    state=states.UserManager.preview_add_points,
)
