from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

DELETE_BUTTON = InlineKeyboardBuilder().add(
    InlineKeyboardButton(text="👀 Прочитано", callback_data="delete")
)
