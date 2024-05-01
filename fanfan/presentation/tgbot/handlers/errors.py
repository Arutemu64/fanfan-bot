import logging

from aiogram import Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import ExceptionTypeFilter
from aiogram.types import ErrorEvent
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_dialog import DialogManager, ShowMode, StartMode
from aiogram_dialog.api.exceptions import UnknownIntent, UnknownState
from sentry_sdk import capture_exception

from fanfan.application.exceptions import UnhandledError
from fanfan.presentation.tgbot.buttons import DELETE_BUTTON
from fanfan.presentation.tgbot.dialogs import states

logger = logging.getLogger(__name__)


async def on_unknown_intent(event, dialog_manager: DialogManager):
    logging.error("Restarting dialog: %s", event.exception)
    await dialog_manager.start(
        states.MAIN.HOME,
        mode=StartMode.RESET_STACK,
        show_mode=ShowMode.SEND,
    )


async def on_unknown_state(event, dialog_manager: DialogManager):
    logging.error("Restarting dialog: %s", event.exception)
    await dialog_manager.start(
        states.MAIN.HOME,
        mode=StartMode.RESET_STACK,
        show_mode=ShowMode.SEND,
    )


async def on_unknown_error(event: ErrorEvent, dialog_manager: DialogManager):
    capture_exception(event.exception)
    logger.critical("Critical error caused by %s", event.exception, exc_info=True)
    if event.update.callback_query:
        user_id = event.update.callback_query.from_user.id
        await event.update.callback_query.message.answer(
            UnhandledError(
                exception=event.exception,
                user_id=user_id,
            ).message,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardBuilder([[DELETE_BUTTON]]).as_markup(),
        )
    elif event.update.message:
        user_id = event.update.message.from_user.id
        await event.update.message.answer(
            UnhandledError(
                exception=event.exception,
                user_id=user_id,
            ).message,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardBuilder([[DELETE_BUTTON]]).as_markup(),
        )


def register_error_handlers(dp: Dispatcher):
    dp.errors.register(on_unknown_intent, ExceptionTypeFilter(UnknownIntent))
    dp.errors.register(on_unknown_state, ExceptionTypeFilter(UnknownState))
    dp.errors.register(on_unknown_error, ExceptionTypeFilter(Exception))
