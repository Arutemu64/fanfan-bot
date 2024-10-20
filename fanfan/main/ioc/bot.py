from collections.abc import AsyncIterable

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.base import BaseEventIsolation, BaseStorage
from aiogram_dialog import BgManagerFactory, setup_dialogs
from aiogram_dialog.api.entities import DIALOG_EVENT_NAME
from aiogram_dialog.context.media_storage import MediaIdStorage
from dishka import Provider, Scope, provide
from dishka.integrations.aiogram import setup_dishka
from sulguk import AiogramSulgukMiddleware

from fanfan.adapters.config_reader import BotConfig
from fanfan.presentation.tgbot import dialogs, handlers
from fanfan.presentation.tgbot.handlers.errors import register_error_handlers
from fanfan.presentation.tgbot.middlewares import (
    LoadDataMiddleware,
    RetryRequestMiddleware,
)


class BotProvider(Provider):
    scope = Scope.APP

    @provide
    async def get_bot(self, config: BotConfig) -> AsyncIterable[Bot]:
        bot = Bot(
            token=config.token.get_secret_value(),
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )
        bot.session.middleware(RetryRequestMiddleware())
        bot.session.middleware(AiogramSulgukMiddleware())
        async with bot:
            yield bot


class DpProvider(Provider):
    scope = Scope.APP

    @provide
    async def get_dispatcher(
        self,
        storage: BaseStorage,
        event_isolation: BaseEventIsolation,
    ) -> AsyncIterable[Dispatcher]:
        dp = Dispatcher(
            storage=storage,
            events_isolation=event_isolation,
        )

        # Bot only works in DM
        dp.message.filter(F.chat.type == "private")

        # Setup DI
        from fanfan.main.di import create_bot_container

        container = create_bot_container()
        setup_dishka(container, dp)

        # Setup dialogs
        dp["bgm_factory"] = setup_dialogs(
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

        yield dp

        await container.close()

    @provide
    def get_bg_manager_factory(self, dp: Dispatcher) -> BgManagerFactory:
        return dp["bgm_factory"]
