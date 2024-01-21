from typing import Optional, Tuple

from aiogram import Dispatcher, F
from aiogram.fsm.storage.base import BaseEventIsolation, BaseStorage
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.strategy import FSMStrategy
from aiogram_dialog import BgManagerFactory, setup_dialogs
from aiogram_dialog.context.media_storage import MediaIdStorage

from fanfan.presentation.tgbot import dialogs, handlers
from fanfan.presentation.tgbot.handlers.errors import register_error_handlers
from fanfan.presentation.tgbot.middlewares import UOWMiddleware
from fanfan.presentation.tgbot.middlewares.userdata import UserDataMiddleware


def create_dispatcher(
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

    dp.update.middleware(UOWMiddleware())
    dp.update.middleware(UserDataMiddleware())

    dp.include_router(handlers.setup_router())
    dp.include_router(dialogs.setup_router())
    register_error_handlers(dp)

    return dp, dialog_bg_factory
