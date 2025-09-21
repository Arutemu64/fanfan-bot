from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.input import ManagedTextInput, TextInput
from aiogram_dialog.widgets.kbd import Button, SwitchTo
from aiogram_dialog.widgets.text import Const, Jinja
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from fanfan.application.quest.add_points_to_user import (
    AddPointsToUser,
    AddPointsToUserDTO,
)
from fanfan.core.exceptions.tickets import TicketNotLinked
from fanfan.core.utils.pluralize import POINTS_PLURALS, pluralize
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.utils import get_dialog_data_adapter
from fanfan.presentation.tgbot.dialogs.user_manager.common import (
    selected_user_getter,
)
from fanfan.presentation.tgbot.dialogs.user_manager.data import UserManagerDialogData
from fanfan.presentation.tgbot.static import strings

MAX_POINTS = 30


async def preview_add_points_getter(
    dialog_manager: DialogManager,
    **kwargs,
):
    dialog_data_adapter = get_dialog_data_adapter(dialog_manager)
    dialog_data = dialog_data_adapter.load(UserManagerDialogData)
    return {
        "points": dialog_data.points,
        "points_pluralized": pluralize(dialog_data.points, POINTS_PLURALS),
        "comment": dialog_data.comment,
    }


async def set_points_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: int,
) -> None:
    dialog_data_adapter = get_dialog_data_adapter(dialog_manager)
    dialog_data = dialog_data_adapter.load(UserManagerDialogData)
    if 0 < data <= MAX_POINTS:
        dialog_data.points = data
        dialog_data_adapter.flush(dialog_data)
        await dialog_manager.switch_to(states.UserManager.SET_COMMENT)
        return
    await message.answer(f"⚠️ Количество очков должно быть от 0 до {MAX_POINTS}")


async def set_comment_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: str,
) -> None:
    dialog_data_adapter = get_dialog_data_adapter(dialog_manager)
    dialog_data = dialog_data_adapter.load(UserManagerDialogData)
    dialog_data.comment = data
    dialog_data_adapter.flush(dialog_data)
    await dialog_manager.switch_to(states.UserManager.PREVIEW_ADD_POINTS)


@inject
async def add_points_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
    add_points: FromDishka[AddPointsToUser],
) -> None:
    dialog_data_adapter = get_dialog_data_adapter(manager)
    dialog_data = dialog_data_adapter.load(UserManagerDialogData)
    try:
        await add_points(
            AddPointsToUserDTO(
                user_id=dialog_data.selected_user_id,
                points=dialog_data.points,
                comment=dialog_data.comment,
            )
        )
        await callback.answer("✅ Успешно")
        await manager.switch_to(states.UserManager.USER_INFO)
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
        state=states.UserManager.USER_INFO,
    ),
    state=states.UserManager.SET_POINTS,
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
        state=states.UserManager.SET_POINTS,
    ),
    state=states.UserManager.SET_COMMENT,
)


preview_add_points_window = Window(
    Const("Давай всё проверим..."),
    Const(" "),
    Jinja(
        "💰 <b>{{ selected_user_username|e }}</b> "
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
        Const(strings.buttons.back), id="back", state=states.UserManager.SET_COMMENT
    ),
    getter=[preview_add_points_getter, selected_user_getter],
    state=states.UserManager.PREVIEW_ADD_POINTS,
)
