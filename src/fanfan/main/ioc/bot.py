from collections.abc import AsyncIterable

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.base import BaseEventIsolation, BaseStorage
from aiogram_dialog import BgManagerFactory
from aiogram_dialog.manager.manager_middleware import BG_FACTORY_KEY
from dishka import Provider, Scope, provide

from fanfan.adapters.config.models import Configuration
from fanfan.presentation.tgbot.config import BotConfig
from fanfan.presentation.tgbot.factory import create_bot, create_dispatcher
from fanfan.presentation.tgbot.utils.cmd_updater import CMDUpdater
from fanfan.presentation.tgbot.utils.qr_reader import QRReader


class BotProvider(Provider):
    scope = Scope.APP

    @provide
    def get_bot_config(self, config: Configuration) -> BotConfig:
        return config.bot

    @provide
    async def get_bot(self, config: BotConfig) -> AsyncIterable[Bot]:
        bot = create_bot(config)
        async with bot:
            yield bot


class DpProvider(Provider):
    scope = Scope.APP

    @provide
    def get_dispatcher(
        self,
        storage: BaseStorage,
        event_isolation: BaseEventIsolation,
    ) -> Dispatcher:
        return create_dispatcher(
            storage=storage,
            event_isolation=event_isolation,
        )

    @provide
    def get_bg_manager_factory(self, dp: Dispatcher) -> BgManagerFactory:
        return dp[BG_FACTORY_KEY]


class BotUtilsProvider(Provider):
    code_processor = provide(QRReader, scope=Scope.REQUEST)
    cmd_updater = provide(CMDUpdater, scope=Scope.REQUEST)
