import operator
from datetime import datetime
from typing import Any

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
from pytz import timezone

from fanfan.application.dto.notification import UserNotification
from fanfan.application.exceptions import ServiceError
from fanfan.application.holder import AppHolder
from fanfan.common.enums import UserRole
from fanfan.common.utils import NOTIFICATIONS_PLURALS, pluralize
from fanfan.config import get_config
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


async def send_delivery_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
):
    app: AppHolder = manager.middleware_data["app"]
    roles_picker: ManagedMultiselect[UserRole] = manager.find(ID_ROLES_PICKER)

    roles = roles_picker.get_checked()
    notifications = []
    timestamp = datetime.now(tz=timezone(get_config().bot.timezone))

    try:
        for u in await app.users.get_all_by_roles(roles):
            notifications.append(
                UserNotification(
                    user_id=u.id,
                    text=manager.dialog_data[DATA_TEXT],
                    bottom_text=f"Отправил @{manager.event.from_user.username}",
                    image_id=manager.dialog_data.get(DATA_IMAGE_ID),
                    timestamp=timestamp,
                ),
            )
        delivery_info = await app.notifications.send_notifications(notifications)
    except ServiceError as e:
        await callback.answer(e.message)
        return

    await callback.message.answer(
        "✅ Рассылка запущена!\n"
        f"Будет отправлено {delivery_info.count} "
        f"{pluralize(delivery_info.count, NOTIFICATIONS_PLURALS)}\n"
        f"Уникальный ID рассылки: <code>{delivery_info.delivery_id}</code>",
    )
    await manager.switch_to(states.DELIVERIES.MAIN)


async def create_delivery_getter(dialog_manager: DialogManager, **kwargs):
    roles_picker: ManagedMultiselect[UserRole] = dialog_manager.find(ID_ROLES_PICKER)
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
        and len(roles_picker.get_checked()) > 0,
    }


async def message_handler(
    message: Message,
    message_input: MessageInput,
    manager: DialogManager,
):
    if message.text or message.caption:
        manager.dialog_data[DATA_TEXT] = message.text or message.caption
    if message.photo:
        manager.dialog_data[DATA_IMAGE_ID] = message.photo[-1].file_id


async def delete_image_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
):
    manager.dialog_data[DATA_IMAGE_ID] = None


async def delete_delivery_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: str,
):
    app: AppHolder = dialog_manager.middleware_data["app"]

    try:
        delivery_info = await app.notifications.delete_delivery(data)
        await message.answer(
            f"✅ Будет удалено {delivery_info.count} "
            f"{pluralize(delivery_info.count, NOTIFICATIONS_PLURALS)}"
        )
    except ServiceError as e:
        await message.answer(e.message)

    await dialog_manager.switch_to(states.DELIVERIES.MAIN)


create_delivery_window = Window(
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
        on_click=send_delivery_handler,
        when="sending_allowed",
    ),
    MessageInput(
        func=message_handler,
    ),
    SwitchTo(
        Const(strings.buttons.back),
        id="back",
        state=states.DELIVERIES.MAIN,
    ),
    getter=create_delivery_getter,
    state=states.DELIVERIES.CREATE,
)

delete_delivery_window = Window(
    Const("🗑️ Отправьте уникальный ID рассылки, которую нужно удалить"),
    TextInput(
        id=ID_QUEUE_ID_INPUT,
        type_factory=str,
        on_success=delete_delivery_handler,
    ),
    SwitchTo(
        Const(strings.buttons.back),
        id="back",
        state=states.DELIVERIES.MAIN,
    ),
    state=states.DELIVERIES.DELETE,
)

main_delivery_window = Window(
    Title(Const("✉️ Рассылки")),
    SwitchTo(
        Const("💌 Создать рассылку"),
        id="create_notification",
        state=states.DELIVERIES.CREATE,
    ),
    SwitchTo(
        Const("🗑️ Удалить рассылку"),
        id="delete_notification",
        state=states.DELIVERIES.DELETE,
    ),
    Cancel(id="org_main_window", text=Const(strings.buttons.back)),
    state=states.DELIVERIES.MAIN,
)


async def _on_dialog_start(start_data: Any, manager: DialogManager):
    manager.dialog_data[DATA_TEXT] = None
    manager.dialog_data[DATA_IMAGE_ID] = None


dialog = Dialog(
    main_delivery_window,
    create_delivery_window,
    delete_delivery_window,
    on_start=_on_dialog_start,
)
