import logging

from aiogram import Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import ExceptionTypeFilter
from aiogram.types import ErrorEvent
from aiogram_dialog import DialogManager
from aiogram_dialog.api.exceptions import UnknownIntent, UnknownState
from sentry_sdk import capture_exception

from fanfan.application.exceptions import UnhandledError
from fanfan.presentation.tgbot.dialogs.widgets import DELETE_BUTTON


async def on_unknown_intent_or_state(event: ErrorEvent, dialog_manager: DialogManager):
    message = "⌛⚠️ Ваша сессия истекла, перезапустите бота командой /start"
    if event.update.callback_query:
        await event.update.callback_query.message.answer(message)
    elif event.update.message:
        await event.update.message.answer(message)


async def on_unknown_error(event: ErrorEvent, dialog_manager: DialogManager):
    capture_exception(event.exception)
    logging.critical("Critical error caused by %s", event.exception, exc_info=True)
    if event.update.callback_query:
        user_id = event.update.callback_query.from_user.id
        await event.update.callback_query.message.answer(
            UnhandledError(
                exception_name=type(event.exception).__name__, user_id=user_id
            ).message,
            parse_mode=ParseMode.HTML,
            reply_markup=DELETE_BUTTON.as_markup(),
        )
    elif event.update.message:
        user_id = event.update.message.from_user.id
        await event.update.message.answer(
            UnhandledError(
                exception_name=type(event.exception).__name__, user_id=user_id
            ).message,
            parse_mode=ParseMode.HTML,
            reply_markup=DELETE_BUTTON.as_markup(),
        )


def register_error_handlers(dp: Dispatcher):
    dp.errors.register(on_unknown_intent_or_state, ExceptionTypeFilter(UnknownIntent))
    dp.errors.register(on_unknown_intent_or_state, ExceptionTypeFilter(UnknownState))
    dp.errors.register(on_unknown_error, ExceptionTypeFilter(Exception))
