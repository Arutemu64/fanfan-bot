from typing import Optional

from aiogram import Dispatcher, F
from aiogram.filters import ExceptionTypeFilter
from aiogram.fsm.storage.base import BaseEventIsolation, BaseStorage
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import DefaultKeyBuilder, RedisStorage
from aiogram.fsm.strategy import FSMStrategy
from aiogram.types import ErrorEvent
from aiogram_dialog import DialogManager, setup_dialogs
from aiogram_dialog.api.exceptions import UnknownIntent, UnknownState
from aiogram_dialog.context.media_storage import MediaIdStorage
from redis.asyncio.client import Redis

from src.bot import commands, dialogs
from src.bot.middlewares import CacheMiddleware, DatabaseMiddleware, UserData
from src.cache import Cache
from src.config import conf
from src.db.database import create_session_maker


def get_redis_storage(
    redis: Redis, state_ttl=conf.redis.state_ttl, data_ttl=conf.redis.data_ttl
):
    return RedisStorage(
        redis=redis,
        state_ttl=state_ttl,
        data_ttl=data_ttl,
        key_builder=DefaultKeyBuilder(with_destiny=True),
    )


async def on_unknown_intent_or_state(event: ErrorEvent, dialog_manager: DialogManager):
    await event.update.callback_query.message.answer(
        "⌛ Ваша сессия истекла, перезапустите бота командой /start"
    )


def get_dispatcher(
    storage: BaseStorage = MemoryStorage(),
    fsm_strategy: Optional[FSMStrategy] = FSMStrategy.CHAT,
    event_isolation: Optional[BaseEventIsolation] = None,
) -> Dispatcher:
    dp = Dispatcher(
        storage=storage, fsm_strategy=fsm_strategy, events_isolation=event_isolation
    )

    dp.message.filter(F.chat.type == "private")

    session_pool = create_session_maker()
    dp.update.middleware(DatabaseMiddleware(session_pool=session_pool))

    client_cache = Cache()
    dp.update.middleware(CacheMiddleware(cache=client_cache))

    dp.update.middleware(UserData())

    dp.include_router(commands.setup_router())
    dp.include_router(dialogs.setup_router())

    mediastorage = MediaIdStorage()

    setup_dialogs(dp, media_id_storage=mediastorage)

    dp.errors.register(
        on_unknown_intent_or_state,
        ExceptionTypeFilter(UnknownIntent),
    )
    dp.errors.register(
        on_unknown_intent_or_state,
        ExceptionTypeFilter(UnknownState),
    )

    return dp
