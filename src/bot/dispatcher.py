from typing import Optional

from aiogram import Dispatcher, F
from aiogram.fsm.storage.base import BaseEventIsolation, BaseStorage
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.strategy import FSMStrategy
from aiogram_dialog import setup_dialogs

from src.bot import commands, dialogs
from src.bot.middlewares import DatabaseMiddleware, UserData
from src.db.database import create_session_maker


def get_dispatcher(
    storage: BaseStorage = MemoryStorage(),
    fsm_strategy: Optional[FSMStrategy] = FSMStrategy.CHAT,
    event_isolation: Optional[BaseEventIsolation] = None,
) -> Dispatcher:
    """This function set up dispatcher with routers, filters and middlewares"""
    dp = Dispatcher(
        storage=storage, fsm_strategy=fsm_strategy, events_isolation=event_isolation
    )

    dp.message.filter(F.chat.type == "private")

    session_pool = create_session_maker()
    dp.update.middleware(DatabaseMiddleware(session_pool=session_pool))
    dp.update.middleware(UserData())

    setup_dialogs(dp)
    dp.include_router(commands.setup_router())
    dp.include_router(dialogs.setup_router())

    return dp
