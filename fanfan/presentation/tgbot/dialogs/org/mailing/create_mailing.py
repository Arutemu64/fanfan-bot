import operator
import typing

from aiogram.enums import ContentType
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, ShowMode, Window
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
from aiogram_dialog.widgets.text import Const, Format

from fanfan.application.mailing.create_mailing import CreateMailing, CreateMailingDTO
from fanfan.core.enums import UserRole
from fanfan.core.exceptions.base import AppException
from fanfan.core.utils.pluralize import NOTIFICATIONS_PLURALS, pluralize
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.getters import roles_getter
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.ui import strings

if typing.TYPE_CHECKING:
    from dishka import AsyncContainer

ID_TEXT_INPUT = "id_text_input"
ID_ROLES_PICKER = "id_roles_picker"

DATA_TEXT = "data_text"
DATA_IMAGE_ID = "data_image_id"
DATA_ROLE_IDS = "data_role_ids"


async def create_mailing_getter(dialog_manager: DialogManager, **kwargs):
    roles_picker: ManagedMultiselect[UserRole] = dialog_manager.find(ID_ROLES_PICKER)
    mailing_text = dialog_manager.dialog_data.get(DATA_TEXT) or "не задан"
    if dialog_manager.dialog_data.get(DATA_IMAGE_ID):
        image = MediaAttachment(
            type=ContentType.PHOTO,
            file_id=MediaId(dialog_manager.dialog_data.get(DATA_IMAGE_ID)),
        )
    else:
        image = None
    return {
        "mailing_text": mailing_text,
        "image": image,
        "sending_allowed": dialog_manager.dialog_data.get(DATA_TEXT)
        and len(roles_picker.get_checked()) > 0,
    }


async def send_mailing_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    container: AsyncContainer = manager.middleware_data["container"]
    roles_picker: ManagedMultiselect[UserRole] = manager.find(ID_ROLES_PICKER)
    create_mailing: CreateMailing = await container.get(CreateMailing)

    try:
        mailing_info = await create_mailing(
            CreateMailingDTO(
                text=manager.dialog_data[DATA_TEXT],
                roles=roles_picker.get_checked(),
                image_id=manager.dialog_data.get(DATA_IMAGE_ID),
            )
        )
        await callback.message.answer(
            "✅ Рассылка запущена!\n"
            f"Будет отправлено {mailing_info.count} "
            f"{pluralize(mailing_info.count, NOTIFICATIONS_PLURALS)}\n"
            f"Уникальный ID рассылки: <code>{mailing_info.mailing_id}</code>",
        )
        await manager.switch_to(states.Mailing.main, show_mode=ShowMode.DELETE_AND_SEND)
    except AppException as e:
        await callback.answer(e.message)
        return


async def message_handler(
    message: Message,
    message_input: MessageInput,
    manager: DialogManager,
) -> None:
    if message.text or message.caption:
        manager.dialog_data[DATA_TEXT] = message.text or message.caption
    if message.photo:
        manager.dialog_data[DATA_IMAGE_ID] = message.photo[-1].file_id


async def delete_image_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    manager.dialog_data[DATA_IMAGE_ID] = None


create_mailing_window = Window(
    Title(Const("✉️ Создание рассылки")),
    Format("Текст: <blockquote>{mailing_text}</blockquote>\n"),
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
        Const("📤 Отправить"),
        id="send",
        on_click=send_mailing_handler,
        when="sending_allowed",
    ),
    MessageInput(
        func=message_handler,
    ),
    SwitchTo(
        Const(strings.buttons.back),
        id="back",
        state=states.Mailing.main,
    ),
    getter=[create_mailing_getter, roles_getter],
    state=states.Mailing.create_mailing,
)
