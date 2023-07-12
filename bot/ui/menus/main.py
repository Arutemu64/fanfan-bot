import random
from pathlib import Path

from aiogram import types
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.config import conf
from bot.db.models import User
from bot.handlers.cb_factories import OpenMenu, ShowActivity, ShowSchedule
from bot.models import Menu
from bot.ui import strings
from bot.ui.strings.menus import quotes

path = Path(__file__).parent.parent / "images" / "test.jpg"


async def show(message: Message, user: User):
    menu = Menu()
    menu.title = "📃 Главное меню"
    menu.text = strings.menus.main_menu_text(first_name=message.chat.first_name)
    menu.bottom = random.choice(quotes)
    # menu.image = path
    menu.keyboard = keyboard(user_group=user.role)
    await menu.show(message)


def keyboard(user_group):
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(
            text=strings.buttons.changelog_channel,
            url="https://t.me/fanfan_bot_dev_notes",
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text=strings.buttons.notifications_channel, url=conf.bot.channel_link
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text=strings.buttons.show_schedule, callback_data=ShowSchedule().pack()
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text=strings.buttons.activities_menu, callback_data=ShowActivity().pack()
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text=strings.buttons.voting,
            callback_data=OpenMenu(menu="nominations").pack(),
        )
    )
    helper_button = types.InlineKeyboardButton(
        text=strings.buttons.helper_menu, callback_data=OpenMenu(menu="helper").pack()
    )
    org_button = types.InlineKeyboardButton(
        text=strings.buttons.org_menu, callback_data=OpenMenu(menu="org").pack()
    )
    match user_group:
        case "helper":
            builder.row(helper_button)
        case "org":
            builder.row(helper_button, org_button)
    return builder.as_markup()
