from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.base import BaseEventIsolation, BaseStorage, DefaultKeyBuilder
from aiogram.fsm.storage.redis import RedisEventIsolation, RedisStorage
from aiogram_dialog import setup_dialogs
from aiogram_dialog.context.media_storage import MediaIdStorage
from aiogram_dialog.manager.manager_middleware import BG_FACTORY_KEY
from dishka import AsyncContainer
from dishka.integrations.aiogram import setup_dishka
from redis.asyncio import Redis
from sulguk import AiogramSulgukMiddleware

from fanfan.adapters.config.models import BotFeatures
from fanfan.adapters.redis.config import RedisConfig
from fanfan.presentation.tgbot.config import BotConfig
from fanfan.presentation.tgbot.dialogs import setup_dialog_router
from fanfan.presentation.tgbot.handlers import setup_handlers_router
from fanfan.presentation.tgbot.handlers.common.errors import register_error_handlers
from fanfan.presentation.tgbot.middlewares import (
    DialogDataAdapterMiddleware,
    LoadCurrentUserMiddleware,
    RetryRequestMiddleware,
    UpdateUserCommandsMiddleware,
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
    container: AsyncContainer,
    bot_features: BotFeatures,
) -> Dispatcher:
    dp = Dispatcher(
        storage=storage,
        events_isolation=event_isolation,
    )

    # Bot only works in DM
    dp.message.filter(F.chat.type == "private")

    # Setup DI
    setup_dishka(container, dp)

    # Setup dialogs
    dp[BG_FACTORY_KEY] = setup_dialogs(
        dp,
        media_id_storage=MediaIdStorage(),
        events_isolation=event_isolation,
    )

    # Setup handlers
    register_error_handlers(dp)
    dp.include_router(
        setup_handlers_router(bot_features)
    )  # Handlers must be above dialogs
    dp.include_router(setup_dialog_router(bot_features))

    # Setup middlewares
    dp.update.outer_middleware(LoadCurrentUserMiddleware())
    dp.update.middleware(UpdateUserCommandsMiddleware())
    for observer in dp.observers.values():
        observer.middleware(DialogDataAdapterMiddleware())

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
