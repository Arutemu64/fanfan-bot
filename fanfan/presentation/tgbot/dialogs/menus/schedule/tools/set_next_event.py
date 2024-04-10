from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button

from fanfan.application.exceptions import ServiceError
from fanfan.application.holder import AppHolder
from fanfan.common.utils import NOTIFICATIONS_PLURALS, pluralize
from fanfan.presentation.tgbot.dialogs.menus.schedule import show_event_page
from fanfan.presentation.tgbot.dialogs.widgets import get_delete_delivery_button


async def set_next_event_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
):
    app: AppHolder = manager.middleware_data["app"]

    try:
        event, delivery_info = await app.schedule_mgmt.set_next_event()
    except ServiceError as e:
        await callback.answer(e.message, show_alert=True)
        return

    await callback.message.answer(
        f"✅ Выступление {event.title} отмечено текущим\n"
        f"Будет отправлено {delivery_info.count} "
        f"{pluralize(delivery_info.count, NOTIFICATIONS_PLURALS)}\n",
        reply_markup=InlineKeyboardBuilder(
            [[get_delete_delivery_button(delivery_info.delivery_id)]]
        ).as_markup(),
    )
    await show_event_page(manager, event.id)
