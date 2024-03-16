from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.fsm.storage.base import BaseEventIsolation, BaseStorage
from aiogram.fsm.storage.redis import (
    DefaultKeyBuilder,
    RedisEventIsolation,
    RedisStorage,
)
from aiogram_dialog import BgManagerFactory, setup_dialogs
from aiogram_dialog.context.media_storage import MediaIdStorage
from aiogram_dialog.manager.bg_manager import BgManagerFactoryImpl
from dishka import Provider, Scope, make_async_container, provide
from dishka.integrations.aiogram import setup_dishka
from redis.asyncio import Redis

from fanfan.config import BotConfig, RedisConfig
from fanfan.presentation.tgbot import dialogs, handlers
from fanfan.presentation.tgbot.handlers.errors import register_error_handlers
from fanfan.presentation.tgbot.middlewares import ContainerMiddleware, RetryMiddleware


class BotProvider(Provider):
    scope = Scope.APP

    @provide
    def get_bot(self, config: BotConfig) -> Bot:
        bot = Bot(token=config.token.get_secret_value(), parse_mode=ParseMode.HTML)
        bot.session.middleware(RetryMiddleware())
        return bot


class DpProvider(Provider):
    scope = Scope.APP

    @provide
    def get_dispatcher(
        self,
        storage: BaseStorage,
        event_isolation: BaseEventIsolation,
    ) -> Dispatcher:
        dp = Dispatcher(
            storage=storage,
            events_isolation=event_isolation,
        )

        dp.message.filter(F.chat.type == "private")

        media_storage = MediaIdStorage()
        setup_dialogs(dp, media_id_storage=media_storage)

        from fanfan.infrastructure.di import get_bot_providers

        bot_container = make_async_container(*get_bot_providers())
        setup_dishka(bot_container, dp)
        dp.update.middleware(ContainerMiddleware())

        dp.include_router(handlers.setup_router())
        dp.include_router(dialogs.setup_router())
        register_error_handlers(dp)

        return dp

    @provide
    def get_bg_manager_factory(self, dp: Dispatcher) -> BgManagerFactory:
        return BgManagerFactoryImpl(dp)

    @provide
    def create_storage(self, redis: Redis, config: RedisConfig) -> BaseStorage:
        return RedisStorage(
            redis=redis,
            state_ttl=config.state_ttl,
            data_ttl=config.data_ttl,
            key_builder=DefaultKeyBuilder(with_destiny=True),
        )

    @provide
    def get_event_isolation(self, redis: Redis) -> BaseEventIsolation:
        return RedisEventIsolation(redis)
