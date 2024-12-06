from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.input import ManagedTextInput, TextInput
from aiogram_dialog.widgets.kbd import Button, Counter, ManagedCounter, SwitchTo
from aiogram_dialog.widgets.text import Const, Jinja
from dishka import AsyncContainer

from fanfan.application.quest.add_points import AddPoints, AddPointsDTO
from fanfan.core.exceptions.users import TicketNotLinked
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.user_manager.common import DATA_USER_ID
from fanfan.presentation.tgbot.ui import strings

ID_ADD_POINTS_COUNTER = "add_points_counter"
COMMENT = "add_points_comment"


async def add_points_getter(
    dialog_manager: DialogManager,
    container: AsyncContainer,
    **kwargs,
):
    counter: ManagedCounter = dialog_manager.find(ID_ADD_POINTS_COUNTER)
    comment = dialog_manager.dialog_data.get(COMMENT)
    return {"comment": comment, "ready_to_add": (counter.get_value() > 0) and comment}


async def add_comment_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: str,
) -> None:
    dialog_manager.dialog_data[COMMENT] = data


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
                comment=manager.dialog_data.get(COMMENT),
            )
        )
        await manager.switch_to(states.UserManager.user_info)
    except TicketNotLinked:
        await callback.answer("⚠️ У участника не привязан билет", show_alert=True)


add_points_window = Window(
    Const(
        "💰 С помощью счетчика укажите, сколько очков получит участник, "
        "и отправьте сообщение с пояснением, за что они будут начислены"
    ),
    Const(" "),
    Const("💬 Комментарий:"),
    Jinja("<blockquote>{{ comment or 'Отправьте комментарий...' }}</blockquote>"),
    Const(" "),
    Const("<i>(Ваш комментарий увидят участник и организаторы)</i>"),
    Counter(
        id=ID_ADD_POINTS_COUNTER,
        plus=Const("➕"),
        minus=Const("➖"),
        min_value=0,
        max_value=5,
        default=0,
    ),
    Button(
        Const("✅ Добавить"),
        id="add_points",
        on_click=add_points_handler,
        when="ready_to_add",
    ),
    TextInput(
        id="id_comment_input",
        type_factory=str,
        on_success=add_comment_handler,
    ),
    SwitchTo(
        Const(strings.buttons.back), id="back", state=states.UserManager.user_info
    ),
    getter=[add_points_getter],
    state=states.UserManager.add_points,
)
