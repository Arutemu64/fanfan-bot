from typing import Optional, Tuple

from aiogram import Dispatcher, F
from aiogram.filters import ExceptionTypeFilter
from aiogram.fsm.storage.base import BaseEventIsolation, BaseStorage
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.strategy import FSMStrategy
from aiogram.types import ErrorEvent
from aiogram_dialog import BgManagerFactory, DialogManager, setup_dialogs
from aiogram_dialog.api.exceptions import UnknownIntent, UnknownState
from aiogram_dialog.context.media_storage import MediaIdStorage
from sqlalchemy.orm import sessionmaker

from src.bot import dialogs, handlers
from src.bot.middlewares import (
    DatabaseMiddleware,
    SentryLoggingMiddleware,
)
from src.config import conf
from src.db.database import create_session_maker


async def on_unknown_intent_or_state(event: ErrorEvent, dialog_manager: DialogManager):
    await event.update.callback_query.message.answer(
        "⌛⚠️ Ваша сессия истекла, перезапустите бота командой /start"
    )


def get_dispatcher(
    storage: BaseStorage = MemoryStorage(),
    fsm_strategy: Optional[FSMStrategy] = FSMStrategy.CHAT,
    event_isolation: Optional[BaseEventIsolation] = None,
    session_pool: sessionmaker = create_session_maker(),
) -> Tuple[Dispatcher, BgManagerFactory]:
    dp = Dispatcher(
        storage=storage, fsm_strategy=fsm_strategy, events_isolation=event_isolation
    )

    dp.message.filter(F.chat.type == "private")

    media_storage = MediaIdStorage()
    bgm_factory = setup_dialogs(dp, media_id_storage=media_storage)

    dp.include_router(handlers.setup_router())
    dp.include_router(dialogs.setup_router())

    if conf.bot.sentry_logging_enabled:
        dp.update.middleware(SentryLoggingMiddleware())

    dp.update.middleware(DatabaseMiddleware(session_pool=session_pool))

    dp.errors.register(
        on_unknown_intent_or_state,
        ExceptionTypeFilter(UnknownIntent),
    )
    dp.errors.register(
        on_unknown_intent_or_state,
        ExceptionTypeFilter(UnknownState),
    )

    return dp, bgm_factory
