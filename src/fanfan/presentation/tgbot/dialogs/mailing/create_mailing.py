import operator
import typing

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

from fanfan.application.mailing.create_role_mailing import (
    CreateRoleMailing,
    CreateRoleMailingDTO,
)
from fanfan.core.vo.user import UserRole
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.getters import roles_getter
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.dialogs.mailing.view_mailing import show_mailing_info
from fanfan.presentation.tgbot.static import strings

if typing.TYPE_CHECKING:
    from dishka import AsyncContainer

ID_TEXT_INPUT = "id_text_input"
ID_ROLES_PICKER = "id_roles_picker"

DATA_TEXT = "data_text"
DATA_IMAGE_ID = "data_image_id"
DATA_ROLE_IDS = "data_role_ids"


async def create_mailing_getter(dialog_manager: DialogManager, **kwargs):
    roles_picker: ManagedMultiselect[UserRole] = dialog_manager.find(ID_ROLES_PICKER)
    mailing_text = dialog_manager.dialog_data.get(DATA_TEXT)
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
        "sending_allowed": mailing_text and len(roles_picker.get_checked()) > 0,
    }


async def send_mailing_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    container: AsyncContainer = manager.middleware_data["container"]
    roles_picker: ManagedMultiselect[UserRole] = manager.find(ID_ROLES_PICKER)
    create_mailing: CreateRoleMailing = await container.get(CreateRoleMailing)

    mailing_id = await create_mailing(
        CreateRoleMailingDTO(
            message_text=manager.dialog_data[DATA_TEXT],
            roles=roles_picker.get_checked(),
            image_id=manager.dialog_data.get(DATA_IMAGE_ID),
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
    Jinja("Текст: <blockquote>{{ mailing_text or 'не задан' }}</blockquote>\n"),
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
        when="sending_allowed",
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
