from aiogram import Bot
from aiogram.enums import ParseMode

from fanfan.config import conf
from fanfan.presentation.tgbot.middlewares import RetryMiddleware


def create_bot(
    token: str = conf.bot.token.get_secret_value(),
    parse_mode: ParseMode = ParseMode.HTML,
) -> Bot:
    bot = Bot(token=token, parse_mode=parse_mode)
    bot.session.middleware(RetryMiddleware())
    return bot
