from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from bot.ui import strings


async def sender_kb(current_event_id=None, next_event_id=None):
    builder = InlineKeyboardBuilder()
    callback_data = 'send_announcement'
    if current_event_id:
        callback_data = f"{callback_data} {str(current_event_id)}"
    else:
        callback_data = f"{callback_data} -1"
    if next_event_id:
        callback_data = f"{callback_data} {str(next_event_id)}"
    builder.row(types.InlineKeyboardButton(text=strings.buttons.send,
                                           callback_data=callback_data))
    builder.row(types.InlineKeyboardButton(text=strings.buttons.delete,
                                           callback_data='delete_message'))
    return builder.as_markup()


async def announce_mode_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text=strings.buttons.next))
    builder.row(types.KeyboardButton(text=strings.buttons.show_schedule))
    builder.row(types.KeyboardButton(text=strings.buttons.back))
    return builder.as_markup(resize_keyboard=True)
