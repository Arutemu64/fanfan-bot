from aiogram import Dispatcher
from aiogram.fsm.storage.base import BaseEventIsolation, BaseStorage
from aiogram_dialog import BgManagerFactory
from aiogram_dialog.manager.manager_middleware import BG_FACTORY_KEY
from dishka import AsyncContainer, Provider, Scope, provide

from fanfan.presentation.tgbot.factory import create_dispatcher


class DpProvider(Provider):
    scope = Scope.APP

    @provide
    def get_dispatcher(
        self,
        storage: BaseStorage,
        event_isolation: BaseEventIsolation,
        container: AsyncContainer,
    ) -> Dispatcher:
        return create_dispatcher(
            storage=storage,
            event_isolation=event_isolation,
            container=container,
        )

    @provide
    def get_bg_manager_factory(self, dp: Dispatcher) -> BgManagerFactory:
        return dp[BG_FACTORY_KEY]


class ExternalBgmFactoryProvider(Provider):
    scope = Scope.APP

    @provide
    def get_bg_manager_factory(
        self,
        storage: BaseStorage,
        event_isolation: BaseEventIsolation,
    ) -> BgManagerFactory:
        from fanfan.main.di import create_bot_container  # noqa: PLC0415

        container = create_bot_container()
        dp = create_dispatcher(
            storage=storage,
            event_isolation=event_isolation,
            container=container,
        )
        return dp[BG_FACTORY_KEY]
