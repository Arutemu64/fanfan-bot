from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.ui import strings


async def show(message):
    text = strings.menus.helper_menu_text
    kb = keyboard()
    await message.edit_text(text, reply_markup=kb)


def keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text=strings.buttons.announce_mode,
                                           callback_data='announce_mode'))
    builder.row(types.InlineKeyboardButton(text=strings.buttons.back,
                                           callback_data='open_main_menu'))
    return builder.as_markup()