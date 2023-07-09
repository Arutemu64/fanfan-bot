from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from bot.handlers.cb_factories import SendAnnouncementCallback
from bot.ui import strings


async def sender_kb(current_event_id=None, next_event_id=None):
    builder = InlineKeyboardBuilder()
    callback = SendAnnouncementCallback()
    if current_event_id:
        callback.current_event_id = current_event_id
    if next_event_id:
        callback.next_event_id = next_event_id
    builder.row(
        types.InlineKeyboardButton(
            text=strings.buttons.send, callback_data=callback.pack()
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text=strings.buttons.delete, callback_data="delete_message"
        )
    )
    return builder.as_markup()


async def announce_mode_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text=strings.buttons.next))
    builder.row(types.KeyboardButton(text=strings.buttons.show_schedule))
    builder.row(types.KeyboardButton(text=strings.buttons.back))
    return builder.as_markup(resize_keyboard=True)
