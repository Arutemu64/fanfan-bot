from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.kbd import Button

from fanfan.application.exceptions import ServiceError
from fanfan.application.holder import AppHolder
from fanfan.common.utils import NOTIFICATIONS_PLURALS, pluralize
from fanfan.presentation.tgbot.buttons import (
    PULL_DOWN_DIALOG,
    get_delete_delivery_button,
)
from fanfan.presentation.tgbot.dialogs import states
from fanfan.presentation.tgbot.dialogs.menus.schedule import show_event_page


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
                        PULL_DOWN_DIALOG,
                    ]
                ]
            ).as_markup()
            if delivery_info.count > 0
            else None,
        )
        await show_event_page(manager, event.id)
        await manager.switch_to(
            states.SCHEDULE.MAIN, show_mode=ShowMode.DELETE_AND_SEND
        )
    except ServiceError as e:
        await callback.answer(e.message, show_alert=True)
