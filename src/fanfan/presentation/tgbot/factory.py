from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.base import BaseEventIsolation, BaseStorage, DefaultKeyBuilder
from aiogram.fsm.storage.redis import RedisEventIsolation, RedisStorage
from aiogram_dialog import setup_dialogs
from aiogram_dialog.api.entities import DIALOG_EVENT_NAME
from aiogram_dialog.context.media_storage import MediaIdStorage
from aiogram_dialog.manager.manager_middleware import BG_FACTORY_KEY
from dishka.integrations.aiogram import setup_dishka
from redis.asyncio import Redis
from sulguk import AiogramSulgukMiddleware

from fanfan.adapters.redis.config import RedisConfig
from fanfan.presentation.tgbot import dialogs, handlers
from fanfan.presentation.tgbot.config import BotConfig
from fanfan.presentation.tgbot.handlers.errors import register_error_handlers
from fanfan.presentation.tgbot.middlewares import (
    LoadDataMiddleware,
    RetryRequestMiddleware,
)


def create_bot(config: BotConfig) -> Bot:
    bot = Bot(
        token=config.token.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    bot.session.middleware(RetryRequestMiddleware())
    bot.session.middleware(AiogramSulgukMiddleware())
    return bot


def create_dispatcher(
    storage: BaseStorage,
    event_isolation: BaseEventIsolation,
) -> Dispatcher:
    dp = Dispatcher(
        storage=storage,
        events_isolation=event_isolation,
    )

    # Bot only works in DM
    dp.message.filter(F.chat.type == "private")

    # Setup dialogs
    dp[BG_FACTORY_KEY] = setup_dialogs(
        dp,
        media_id_storage=MediaIdStorage(),
        events_isolation=event_isolation,
    )

    # Setup handlers
    dp.include_router(handlers.setup_router())  # Handlers must be above dialogs
    dp.include_router(dialogs.setup_router())
    register_error_handlers(dp)

    # Setup middlewares
    dp.message.outer_middleware(LoadDataMiddleware())
    dp.callback_query.outer_middleware(LoadDataMiddleware())
    dp.inline_query.outer_middleware(LoadDataMiddleware())
    dp.errors.outer_middleware(LoadDataMiddleware())
    dp.observers[DIALOG_EVENT_NAME].outer_middleware(LoadDataMiddleware())

    # Setup DI
    # We create another container here (instead of using external)
    # cause external container may use different IdProvider
    from fanfan.main.di import create_bot_container

    container = create_bot_container()
    setup_dishka(container, dp)
    dp.shutdown.register(container.close)

    return dp


def create_redis_storage(
    redis: Redis,
    config: RedisConfig,
) -> RedisStorage:
    return RedisStorage(
        redis=redis,
        key_builder=DefaultKeyBuilder(with_destiny=True),
        state_ttl=config.state_ttl,
        data_ttl=config.data_ttl,
    )


def create_redis_isolation(storage: RedisStorage) -> RedisEventIsolation:
    return storage.create_isolation()
