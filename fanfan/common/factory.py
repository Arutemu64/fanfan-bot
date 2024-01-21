from aiogram import Bot
from aiogram.enums import ParseMode

from fanfan.config import conf


def create_bot(
    token: str = conf.bot.token.get_secret_value(),
    parse_mode: ParseMode = ParseMode.HTML,
) -> Bot:
    return Bot(token=token, parse_mode=parse_mode)
