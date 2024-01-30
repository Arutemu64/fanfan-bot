import operator
import uuid
from typing import Any, List

from aiogram.enums import ContentType
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from aiogram_dialog.widgets.input import ManagedTextInput, MessageInput, TextInput
from aiogram_dialog.widgets.kbd import (
    Button,
    Cancel,
    Group,
    ManagedMultiselect,
    Multiselect,
    SwitchTo,
)
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.text import Const, Format

from fanfan.application.dto.common import UserNotification
from fanfan.application.exceptions import ServiceError
from fanfan.application.services import ServicesHolder
from fanfan.common.enums import UserRole
from fanfan.presentation.tgbot.dialogs import states
from fanfan.presentation.tgbot.dialogs.getters import get_roles_list
from fanfan.presentation.tgbot.dialogs.widgets import Title
from fanfan.presentation.tgbot.ui import strings

ID_ROLES_PICKER = "id_roles_picker"
ID_TEXT_INPUT = "id_text_input"
ID_QUEUE_ID_INPUT = "id_queue_id_input"

DATA_TEXT = "data_text"
DATA_IMAGE_ID = "data_image_id"
DATA_ROLE_IDS = "data_role_ids"


async def send_notification_handler(
    callback: CallbackQuery, button: Button, manager: DialogManager
):
    services: ServicesHolder = manager.middleware_data["services"]
    multiselect: ManagedMultiselect = manager.find(ID_ROLES_PICKER)

    roles: List[UserRole] = multiselect.get_checked()
    delivery_id = uuid.uuid4().hex
    notifications = []
    try:
        for u in await services.users.get_all_by_roles(roles):
            notifications.append(
                UserNotification(
                    user_id=u.id,
                    text=manager.dialog_data[DATA_TEXT],
                    bottom_text=f"Отправил @{manager.event.from_user.username}",
                    image_id=manager.dialog_data.get(DATA_IMAGE_ID),
                )
            )
        await services.notifications.send_notifications(notifications, delivery_id)
    except ServiceError as e:
        await callback.answer(e.message)
        return
    await callback.message.answer(
        "✅ Рассылка запущена!\n" f"Уникальный ID рассылки: <code>{delivery_id}</code>"
    )
    await manager.start(states.ORG.MAIN)


async def create_notification_getter(dialog_manager: DialogManager, **kwargs):
    multiselect: ManagedMultiselect = dialog_manager.find(ID_ROLES_PICKER)
    notification_text = dialog_manager.dialog_data[DATA_TEXT] or "не задан"
    if dialog_manager.dialog_data[DATA_IMAGE_ID]:
        image = MediaAttachment(
            type=ContentType.PHOTO,
            file_id=MediaId(dialog_manager.dialog_data[DATA_IMAGE_ID]),
        )
    else:
        image = None
    return {
        "notification_text": notification_text,
        "image": image,
        "roles": get_roles_list(),
        "sending_allowed": dialog_manager.dialog_data[DATA_TEXT]
        and len(multiselect.get_checked()) > 0,
    }


async def message_handler(
    message: Message, message_input: MessageInput, manager: DialogManager
):
    if message.text or message.caption:
        manager.dialog_data[DATA_TEXT] = message.text or message.caption
    if message.photo:
        manager.dialog_data[DATA_IMAGE_ID] = message.photo[-1].file_id


async def delete_image_handler(
    callback: CallbackQuery, button: Button, manager: DialogManager
):
    manager.dialog_data[DATA_IMAGE_ID] = None


async def delete_notification_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: str,
):
    services: ServicesHolder = dialog_manager.middleware_data["services"]

    try:
        count = await services.notifications.delete_delivery(data)
        await message.answer(f"✅ Будет удалено {count} сообщений")
    except ServiceError as e:
        await message.answer(e.message)

    await dialog_manager.switch_to(states.NOTIFICATIONS.MAIN)


create_notification_window = Window(
    Title(Const("✉️ Создание рассылки")),
    Format("Текст рассылки: {notification_text}\n"),
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
        on_click=send_notification_handler,
        when="sending_allowed",
    ),
    MessageInput(
        func=message_handler,
    ),
    SwitchTo(
        Const(strings.buttons.back),
        id="back",
        state=states.NOTIFICATIONS.MAIN,
    ),
    getter=create_notification_getter,
    state=states.NOTIFICATIONS.CREATE,
)

delete_notification_window = Window(
    Const("🗑️ Отправьте уникальный ID рассылки, которую нужно удалить"),
    TextInput(
        id=ID_QUEUE_ID_INPUT,
        type_factory=str,
        on_success=delete_notification_handler,
    ),
    SwitchTo(
        Const(strings.buttons.back),
        id="back",
        state=states.NOTIFICATIONS.MAIN,
    ),
    state=states.NOTIFICATIONS.DELETE,
)

main_notifications_window = Window(
    Title(Const("✉️ Рассылки")),
    SwitchTo(
        Const("💌 Создать рассылку"),
        id="create_notification",
        state=states.NOTIFICATIONS.CREATE,
    ),
    SwitchTo(
        Const("🗑️ Удалить рассылку"),
        id="delete_notification",
        state=states.NOTIFICATIONS.DELETE,
    ),
    Cancel(id="org_main_window", text=Const(strings.buttons.back)),
    state=states.NOTIFICATIONS.MAIN,
)


async def _on_dialog_start(start_data: Any, manager: DialogManager):
    manager.dialog_data[DATA_TEXT] = None
    manager.dialog_data[DATA_IMAGE_ID] = None


dialog = Dialog(
    main_notifications_window,
    create_notification_window,
    delete_notification_window,
    on_start=_on_dialog_start,
)
