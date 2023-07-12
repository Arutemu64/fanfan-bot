from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.handlers.cb_factories import OpenMenu
from bot.models import Menu
from bot.ui import strings


async def show(message):
    menu = Menu()
    menu.title = f"📣 Для волонтёров доступны следующие функции:"
    menu.text = strings.menus.helper_menu_text
    menu.keyboard = keyboard()
    await menu.show(message)


def keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(
            text=strings.buttons.announce_mode, callback_data="announce_mode"
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text=strings.buttons.back, callback_data=OpenMenu(menu="main").pack()
        )
    )
    return builder.as_markup()
