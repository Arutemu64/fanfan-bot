from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.input import ManagedTextInput, TextInput
from aiogram_dialog.widgets.kbd import Button, SwitchTo
from aiogram_dialog.widgets.text import Const, Jinja
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from fanfan.application.mailing.send_message_to_user import (
    SendMessageToUser,
    SendMessageToUserDTO,
)
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.utils import get_dialog_data_adapter
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.dialogs.user_manager.common import (
    selected_user_getter,
)
from fanfan.presentation.tgbot.dialogs.user_manager.data import UserManagerDialogData
from fanfan.presentation.tgbot.middlewares.dialog_data_adapter import DialogDataAdapter
from fanfan.presentation.tgbot.static import strings


async def send_message_getter(
    dialog_manager: DialogManager,
    dialog_data_adapter: DialogDataAdapter,
    **kwargs,
):
    dialog_data = dialog_data_adapter.load(UserManagerDialogData)
    return {
        "message_text": dialog_data.message_text,
        "sending_allowed": bool(dialog_data.message_text),
    }


async def set_message_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: str,
) -> None:
    dialog_data_adapter = get_dialog_data_adapter(dialog_manager)
    dialog_data = dialog_data_adapter.load(UserManagerDialogData)
    dialog_data.message_text = data
    dialog_data_adapter.flush(dialog_data)


@inject
async def send_message_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
    send_message: FromDishka[SendMessageToUser],
) -> None:
    dialog_data_adapter = get_dialog_data_adapter(manager)
    dialog_data = dialog_data_adapter.load(UserManagerDialogData)
    await send_message(
        SendMessageToUserDTO(
            user_id=dialog_data.selected_user_id, message_text=dialog_data.message_text
        )
    )
    await callback.answer("✅ Сообщение отправлено")
    dialog_data.message_text = None
    dialog_data_adapter.flush(dialog_data)
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
    getter=[send_message_getter, selected_user_getter],
    state=states.UserManager.SEND_MESSAGE,
)
