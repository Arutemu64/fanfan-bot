from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.base import BaseEventIsolation, BaseStorage
from aiogram_dialog import BgManagerFactory, setup_dialogs
from dishka import Provider, Scope, provide
from sulguk import AiogramSulgukMiddleware

from fanfan.common.config import BotConfig
from fanfan.infrastructure.scheduler.notifications.bot_notifier import Notifier
from fanfan.presentation.tgbot.middlewares import RetryRequestMiddleware


class BotProvider(Provider):
    scope = Scope.APP

    @provide
    def get_bot(self, config: BotConfig) -> Bot:
        bot = Bot(
            token=config.token.get_secret_value(),
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )
        bot.session.middleware(RetryRequestMiddleware())
        bot.session.middleware(AiogramSulgukMiddleware())
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

        return dp

    @provide(scope=Scope.REQUEST)
    def get_bg_manager_factory(
        self, dp: Dispatcher, event_isolation: BaseEventIsolation
    ) -> BgManagerFactory:
        return setup_dialogs(dp, events_isolation=event_isolation)


class NotifierProvider(Provider):
    scope = Scope.REQUEST

    notifier = provide(Notifier)
