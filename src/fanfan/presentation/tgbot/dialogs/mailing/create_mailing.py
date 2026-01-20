import operator
from typing import Final

from aiogram.enums import ContentType
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import (
    Button,
    Group,
    ManagedMultiselect,
    Multiselect,
    SwitchTo,
)
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.text import Const, Format, Jinja
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from fanfan.application.notifications.create_role_mailing import (
    CreateRoleMailing,
    CreateRoleMailingDTO,
)
from fanfan.core.vo.telegram import TelegramFileId
from fanfan.core.vo.user import UserRole
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.getters import roles_getter
from fanfan.presentation.tgbot.dialogs.common.utils import get_dialog_data_adapter
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.dialogs.mailing.api import show_mailing_info
from fanfan.presentation.tgbot.dialogs.mailing.data import MailingDialogData
from fanfan.presentation.tgbot.middlewares.dialog_data_adapter import DialogDataAdapter
from fanfan.presentation.tgbot.static import strings

ID_TEXT_INPUT: Final[str] = "id_text_input"
ID_ROLES_PICKER: Final[str] = "id_roles_picker"


async def create_mailing_getter(
    dialog_manager: DialogManager, dialog_data_adapter: DialogDataAdapter, **kwargs
):
    dialog_data = dialog_data_adapter.load(MailingDialogData)
    roles_picker: ManagedMultiselect[UserRole] = dialog_manager.find(ID_ROLES_PICKER)
    if dialog_data.image_id:
        image = MediaAttachment(
            type=ContentType.PHOTO,
            file_id=MediaId(dialog_data.image_id),
        )
    else:
        image = None
    return {
        "text": dialog_data.text,
        "image": image,
        "is_sending_allowed": dialog_data.text and len(roles_picker.get_checked()) > 0,
    }


@inject
async def send_mailing_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
    create_mailing: FromDishka[CreateRoleMailing],
) -> None:
    dialog_data_adapter = get_dialog_data_adapter(manager)
    roles_picker: ManagedMultiselect[UserRole] = manager.find(ID_ROLES_PICKER)
    dialog_data = dialog_data_adapter.load(MailingDialogData)
    mailing_id = await create_mailing(
        CreateRoleMailingDTO(
            text=dialog_data.text,
            roles=roles_picker.get_checked(),
            image_id=dialog_data.image_id,
        )
    )
    await callback.message.answer(
        f"✅ Рассылка запущена!\nУникальный ID рассылки: <code>{mailing_id}</code>"
    )
    await show_mailing_info(manager, mailing_id)


async def message_handler(
    message: Message,
    message_input: MessageInput,
    manager: DialogManager,
) -> None:
    dialog_data_adapter = get_dialog_data_adapter(manager)
    dialog_data = dialog_data_adapter.load(MailingDialogData)
    if message.text or message.caption:
        dialog_data.text = message.text or message.caption
    if message.photo:
        dialog_data.image_id = TelegramFileId(message.photo[-1].file_id)
    dialog_data_adapter.flush(dialog_data)


async def delete_image_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    dialog_data_adapter = get_dialog_data_adapter(manager)
    dialog_data = dialog_data_adapter.load(MailingDialogData)
    dialog_data.image_id = None
    dialog_data_adapter.flush(dialog_data)


create_mailing_window = Window(
    Title(Const("✉️ Создание рассылки")),
    Jinja("Текст: <blockquote>{{ text or 'не задан' }}</blockquote>\n"),
    Const("<i>⌨️ Отправьте текст/фото, чтобы добавить его в сообщение.</i>"),
    DynamicMedia(
        selector="image",
        when="image",
    ),
    Button(
        id="delete_image",
        text=Const("🗑️ Удалить изображение"),
        when="image",
        on_click=delete_image_handler,
    ),
    Button(
        id="visual",
        text=Const("Отметьте нужные роли:"),
    ),
    Group(
        Multiselect(
            Format("✓ {item[2]}"),
            Format("{item[2]}"),
            id=ID_ROLES_PICKER,
            item_id_getter=operator.itemgetter(0),
            items="roles",
            type_factory=UserRole,
        ),
        width=2,
    ),
    Button(
        Const(strings.buttons.send),
        id="send",
        on_click=send_mailing_handler,
        when="is_sending_allowed",
    ),
    MessageInput(
        func=message_handler,
    ),
    SwitchTo(
        Const(strings.buttons.back),
        id="back",
        state=states.Mailing.MAIN,
    ),
    getter=[create_mailing_getter, roles_getter],
    state=states.Mailing.CREATE_MAILING,
)
