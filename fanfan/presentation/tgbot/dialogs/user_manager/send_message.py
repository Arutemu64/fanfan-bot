from typing import TYPE_CHECKING

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.input import ManagedTextInput, TextInput
from aiogram_dialog.widgets.kbd import Button, SwitchTo
from aiogram_dialog.widgets.text import Const, Jinja

from fanfan.application.users.send_org_message import SendOrgMessage, SendOrgMessageDTO
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.dialogs.user_manager.common import (
    DATA_USER_ID,
    managed_user_getter,
)
from fanfan.presentation.tgbot.static import strings

if TYPE_CHECKING:
    from dishka import AsyncContainer

MESSAGE_TEXT = "message_text"


async def send_message_getter(
    dialog_manager: DialogManager,
    **kwargs,
):
    message_text = dialog_manager.dialog_data.get(MESSAGE_TEXT)
    return {MESSAGE_TEXT: message_text, "sending_allowed": bool(message_text)}


async def set_message_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: str,
) -> None:
    dialog_manager.dialog_data[MESSAGE_TEXT] = data


async def send_message_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    container: AsyncContainer = manager.middleware_data["container"]
    send_message: SendOrgMessage = await container.get(SendOrgMessage)

    await send_message(
        SendOrgMessageDTO(
            user_id=manager.start_data[DATA_USER_ID],
            message_text=manager.dialog_data[MESSAGE_TEXT],
        )
    )

    await callback.answer("✅ Сообщение отправлено")
    manager.dialog_data[MESSAGE_TEXT] = None
    await manager.switch_to(states.UserManager.USER_INFO)


send_message_window = Window(
    Title(Const(strings.titles.send_message)),
    Const(
        "С помощью этого раздела можно отправить пользователю сообщение "
        "от имени бота. Для двухсторонней связи необходимо использовать "
        "обычные сообщения. Эта функция полезна, если у пользователя не задан "
        "никнейм в настройках Telegram."
    ),
    Const(" "),
    Jinja("Вы собираетесь написать @{{ managed_user.username }}"),
    Const(" "),
    Jinja("Текст: <blockquote>{{ message_text or 'не задан' }}</blockquote>"),
    Button(
        Const(strings.buttons.send),
        id="send",
        on_click=send_message_handler,
        when="sending_allowed",
    ),
    SwitchTo(
        Const(strings.buttons.back),
        id="back",
        state=states.UserManager.USER_INFO,
    ),
    TextInput(
        id="id_set_message_text",
        type_factory=str,
        on_success=set_message_handler,
    ),
    getter=[send_message_getter, managed_user_getter],
    state=states.UserManager.SEND_MESSAGE,
)
