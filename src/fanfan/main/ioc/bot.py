from collections.abc import AsyncIterable

from aiogram import Bot
from dishka import Provider, Scope, provide

from fanfan.adapters.bot.notifier import TelegramNotifier
from fanfan.adapters.config.models import EnvConfig
from fanfan.presentation.tgbot.config import BotConfig
from fanfan.presentation.tgbot.factory import create_bot
from fanfan.presentation.tgbot.utils.code_processor import CodeProcessor


class BotProvider(Provider):
    scope = Scope.APP

    @provide
    def get_bot_config(self, config: EnvConfig) -> BotConfig:
        return config.bot

    @provide
    async def get_bot(self, config: BotConfig) -> AsyncIterable[Bot]:
        bot = create_bot(config)
        async with bot:
            yield bot

    notifier = provide(TelegramNotifier)


class BotUtilsProvider(Provider):
    code_processor = provide(CodeProcessor, scope=Scope.REQUEST)
