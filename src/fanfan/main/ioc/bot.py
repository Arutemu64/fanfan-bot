from collections.abc import AsyncIterable

from aiogram import Bot
from dishka import Provider, Scope, provide

from fanfan.adapters.config.models import Configuration
from fanfan.presentation.tgbot.config import BotConfig
from fanfan.presentation.tgbot.factory import create_bot
from fanfan.presentation.tgbot.utils.cmd_updater import CMDUpdater
from fanfan.presentation.tgbot.utils.code_processor import CodeProcessor


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


class BotUtilsProvider(Provider):
    cmd_updater = provide(CMDUpdater, scope=Scope.REQUEST)
    code_processor = provide(CodeProcessor, scope=Scope.REQUEST)
