from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.input import ManagedTextInput
from aiogram_dialog.widgets.kbd import Button

from fanfan.application.dto.user import FullUserDTO, UpdateUserSettingsDTO
from fanfan.application.exceptions import ServiceError
from fanfan.application.holder import AppHolder
from fanfan.common.utils import NOTIFICATIONS_PLURALS, pluralize
from fanfan.presentation.tgbot import states

from ...buttons import get_delete_delivery_button
from .common import set_search_query, show_event_page, update_schedule


async def schedule_text_input_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: str,
):
    if "/" in data and data.replace("/", "").isnumeric():
        await dialog_manager.start(
            states.EVENT_DETAILS.MAIN, data=int(data.replace("/", ""))
        )
    elif data.isnumeric():
        await show_event_page(dialog_manager, int(data))
    else:
        await set_search_query(dialog_manager, data)


async def subscriptions_text_input_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: str,
):
    if "/" in data and data.replace("/", "").isnumeric():
        await dialog_manager.start(
            states.EVENT_DETAILS.MAIN, data=int(data.replace("/", ""))
        )


async def toggle_all_notifications_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
):
    user: FullUserDTO = manager.middleware_data["user"]
    app: AppHolder = manager.middleware_data["app"]
    try:
        await app.users.update_user_settings(
            UpdateUserSettingsDTO(
                user_id=user.id,
                receive_all_announcements=not user.settings.receive_all_announcements,
            ),
        )
        manager.middleware_data["user"] = await app.users.get_user_by_id(user.id)
    except ServiceError as e:
        await callback.answer(e.message)


async def update_schedule_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
):
    await update_schedule(manager)


async def reset_search_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
):
    await set_search_query(manager, None)


async def set_next_event_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
):
    app: AppHolder = manager.middleware_data["app"]

    try:
        event, delivery_info = await app.schedule_mgmt.set_next_event()
        await callback.message.answer(
            f"✅ Выступление <b>{event.title}</b> отмечено текущим\n"
            f"Будет отправлено {delivery_info.count} "
            f"{pluralize(delivery_info.count, NOTIFICATIONS_PLURALS)}\n"
            f"Уникальный ID рассылки: <code>{delivery_info.delivery_id}</code>",
            reply_markup=InlineKeyboardBuilder(
                [
                    [
                        get_delete_delivery_button(delivery_info.delivery_id),
                    ]
                ]
            ).as_markup()
            if delivery_info.count > 0
            else None,
        )
        await show_event_page(manager, event.id)
        manager.show_mode = ShowMode.DELETE_AND_SEND
    except ServiceError as e:
        await callback.answer(e.message, show_alert=True)
