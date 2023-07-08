from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.db.models import Settings
from bot.handlers.cb_factories import OpenMenu
from bot.ui import strings


async def show(message, settings: Settings):
    text = strings.menus.org_menu_text
    kb = keyboard(settings)
    await message.edit_text(text, reply_markup=kb)


def keyboard(settings: Settings):
    builder = InlineKeyboardBuilder()
    if settings.voting_enabled:
        builder.row(types.InlineKeyboardButton(text=strings.buttons.disable_voting,
                                               callback_data='switch_voting'))
    else:
        builder.row(types.InlineKeyboardButton(text=strings.buttons.enable_voting,
                                               callback_data='switch_voting'))
    builder.row(types.InlineKeyboardButton(text=strings.buttons.back,
                                           callback_data=OpenMenu(menu='main').pack()))
    return builder.as_markup()
