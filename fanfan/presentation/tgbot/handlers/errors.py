import contextlib
import logging
import typing

from aiogram import Dispatcher
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import ExceptionTypeFilter
from aiogram.types import ErrorEvent, ReplyKeyboardRemove
from aiogram_dialog import DialogManager, ShowMode, StartMode
from aiogram_dialog.api.exceptions import OutdatedIntent, UnknownIntent, UnknownState
from sentry_sdk import capture_exception

from fanfan.core.exceptions.base import AppException
from fanfan.core.utils.notifications import create_error_notification
from fanfan.presentation.tgbot import states

logger = logging.getLogger(__name__)


async def on_app_exception(event: ErrorEvent, dialog_manager: DialogManager) -> None:
    exception: AppException = typing.cast(AppException, event.exception)
    if c := event.update.callback_query:
        await c.answer(exception.message, show_alert=True)
    elif m := event.update.message:
        await m.reply(exception.message)
        await dialog_manager.update(data={}, show_mode=ShowMode.DELETE_AND_SEND)


async def on_dialog_error(event: ErrorEvent, dialog_manager: DialogManager) -> None:
    logging.error("Restarting dialog: %s", event.exception)
    msg = "⌛ Ваша сессия истекла, перезапуск бота..."
    if c := event.update.callback_query:
        await c.answer(msg)
        if c.message:
            with contextlib.suppress(TelegramBadRequest):
                await c.message.delete()
    elif m := event.update.message:
        await m.answer(msg, reply_markup=ReplyKeyboardRemove())
    await dialog_manager.start(
        states.Main.home,
        mode=StartMode.RESET_STACK,
        show_mode=ShowMode.DELETE_AND_SEND,
    )


async def on_unknown_error(event: ErrorEvent) -> None:
    capture_exception(event.exception)
    logger.critical(
        "Critical error caused by %s", type(event.exception).__name__, exc_info=True
    )
    notification = create_error_notification(event.exception)
    if c := event.update.callback_query:
        await c.message.answer(
            notification.render_message_text(),
            parse_mode=ParseMode.HTML,
            reply_markup=notification.reply_markup,
        )
    elif m := event.update.message:
        await m.answer(
            notification.render_message_text(),
            parse_mode=ParseMode.HTML,
            reply_markup=notification.reply_markup,
        )


def register_error_handlers(dp: Dispatcher) -> None:
    dp.errors.register(on_dialog_error, ExceptionTypeFilter(UnknownIntent))
    dp.errors.register(on_dialog_error, ExceptionTypeFilter(UnknownState))
    dp.error.register(on_dialog_error, ExceptionTypeFilter(OutdatedIntent))
    dp.errors.register(on_app_exception, ExceptionTypeFilter(AppException))
    dp.errors.register(on_unknown_error, ExceptionTypeFilter(Exception))
