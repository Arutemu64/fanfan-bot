from aiogram import Dispatcher
from aiogram.filters import ExceptionTypeFilter
from aiogram.types import ErrorEvent
from aiogram_dialog import DialogManager
from aiogram_dialog.api.exceptions import UnknownIntent, UnknownState


async def on_unknown_intent_or_state(event: ErrorEvent, dialog_manager: DialogManager):
    await event.update.callback_query.message.answer(
        "⌛⚠️ Ваша сессия истекла, перезапустите бота командой /start"
    )


def register_error_handlers(dp: Dispatcher):
    dp.errors.register(on_unknown_intent_or_state, ExceptionTypeFilter(UnknownIntent))
    dp.errors.register(on_unknown_intent_or_state, ExceptionTypeFilter(UnknownState))
