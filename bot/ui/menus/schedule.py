import math

from aiogram import types
from aiogram.exceptions import TelegramBadRequest
from sqlalchemy.ext.asyncio import AsyncSession

from bot.config import conf
from bot.db.models import Settings, Event
from bot.ui import strings
from bot.handlers.cb_factories import ShowSchedule


async def show(session: AsyncSession, message, show_back_button: bool = False, page: int = None):
    settings = await Settings.get_one(session, True)
    per_page = conf.events_per_page
    if page is None:
        page = math.floor((settings.current_event_id - 1) / per_page)
        if page < 0:
            page = 0
    events = await Event.get_range(session, (page * per_page), (page * per_page) + per_page, Event.id)
    total_pages = math.floor((await Event.count(session, True) / per_page))
    text = f"<b>📅 Расписание</b> (страница {page + 1} из {total_pages + 1})\n\n"
    for event in events:
        entry = ''
        if event.id:
            entry = f"<b>{event.id}.</b> {event.title}"
        if event.id == settings.current_event_id:
            entry = f"""<b>👉 {entry}</b>"""
        text = text + entry + "\n"
    kb = keyboard(page, total_pages, show_back_button)
    try:
        await message.edit_text(text, reply_markup=kb)
    except TelegramBadRequest:
        return


def keyboard(page, total_pages: int, show_back_button: bool = False):
    navigation_buttons = []
    if page > 0:
        navigation_buttons.insert(0, types.InlineKeyboardButton(text="⏪",
                                                                callback_data=ShowSchedule(page=0).pack()))
        navigation_buttons.insert(1, types.InlineKeyboardButton(text="◀️",
                                                                callback_data=ShowSchedule(page=page-1).pack()))
    else:
        navigation_buttons.insert(0, types.InlineKeyboardButton(text="⠀",
                                                                callback_data='dummy'))
        navigation_buttons.insert(1, types.InlineKeyboardButton(text="⠀",
                                                                callback_data='dummy'))
    navigation_buttons.append(types.InlineKeyboardButton(text="🔃",
                                                         callback_data=ShowSchedule().pack()))
    if page < total_pages:
        navigation_buttons.append(types.InlineKeyboardButton(text="▶️",
                                                             callback_data=ShowSchedule(page=page+1).pack()))
        navigation_buttons.append(types.InlineKeyboardButton(text="⏭️",
                                                             callback_data=ShowSchedule(page=total_pages).pack()))
    else:
        navigation_buttons.append(types.InlineKeyboardButton(text="⠀", callback_data='dummy'))
        navigation_buttons.append(types.InlineKeyboardButton(text="⠀", callback_data='dummy'))
    buttons = [navigation_buttons]
    if show_back_button:
        buttons.append([types.InlineKeyboardButton(text=strings.buttons.back,
                                                   callback_data='open_main_menu')])
    kb = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return kb
