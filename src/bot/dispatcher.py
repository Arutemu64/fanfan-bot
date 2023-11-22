from typing import Optional, Tuple

from aiogram import Dispatcher, F
from aiogram.fsm.storage.base import BaseEventIsolation, BaseStorage
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.strategy import FSMStrategy
from aiogram_dialog import BgManagerFactory, setup_dialogs
from aiogram_dialog.context.media_storage import MediaIdStorage

from src.bot import dialogs, handlers
from src.bot.handlers.errors import register_error_handlers
from src.bot.middlewares import (
    DatabaseMiddleware,
    UserDataMiddleware,
)


def get_dispatcher(
    storage: BaseStorage = MemoryStorage(),
    fsm_strategy: Optional[FSMStrategy] = FSMStrategy.CHAT,
    event_isolation: Optional[BaseEventIsolation] = None,
) -> Tuple[Dispatcher, BgManagerFactory]:
    dp = Dispatcher(
        storage=storage, fsm_strategy=fsm_strategy, events_isolation=event_isolation
    )

    dp.message.filter(F.chat.type == "private")

    media_storage = MediaIdStorage()
    dialog_bg_factory = setup_dialogs(dp, media_id_storage=media_storage)

    dp.include_router(handlers.setup_router())
    dp.include_router(dialogs.setup_router())
    register_error_handlers(dp)

    dp.update.middleware(DatabaseMiddleware())
    dp.update.middleware(UserDataMiddleware())

    return dp, dialog_bg_factory
