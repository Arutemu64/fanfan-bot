from datetime import datetime

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import ManagedTextInput, MessageInput
from aiogram_dialog.widgets.kbd import Button, ManagedMultiselect
from pytz import timezone

from fanfan.application.dto.notification import UserNotification
from fanfan.application.exceptions import ServiceError
from fanfan.application.holder import AppHolder
from fanfan.common.enums import UserRole
from fanfan.common.utils import NOTIFICATIONS_PLURALS, pluralize
from fanfan.config import get_config
from fanfan.infrastructure.scheduler.utils.notifications import (
    delete_delivery,
    send_notifications,
)
from fanfan.presentation.tgbot import states

from .constants import (
    DATA_IMAGE_ID,
    DATA_TEXT,
    ID_ROLES_PICKER,
)


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
        delivery_info = await send_notifications(notifications)
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
    delivery_info = await delete_delivery(data)
    await message.answer(
        f"✅ Будет удалено {delivery_info.count} "
        f"{pluralize(delivery_info.count, NOTIFICATIONS_PLURALS)}"
    )

    await dialog_manager.switch_to(states.DELIVERIES.MAIN)
