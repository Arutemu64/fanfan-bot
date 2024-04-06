from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button

from fanfan.application.exceptions import ServiceError
from fanfan.application.holder import AppHolder
from fanfan.presentation.tgbot.dialogs.menus.schedule import show_event_page


async def set_next_event_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
):
    app: AppHolder = manager.middleware_data["app"]

    try:
        event = await app.schedule_mgmt.set_next_event()
    except ServiceError as e:
        await callback.answer(e.message, show_alert=True)
        return

    await callback.answer(f"✅ {event.title}")
    await show_event_page(manager, event.id)
