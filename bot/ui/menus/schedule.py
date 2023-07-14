import math

from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession

from bot.config import conf
from bot.db.models import Event, Settings
from bot.handlers.cb_factories import OpenMenu, ShowSchedule
from bot.models import Menu
from bot.ui import strings


async def show(
    session: AsyncSession, message, show_back_button: bool = False, page: int = None
):
    per_page = conf.events_per_page
    total_pages = math.floor((await Event.count(session, True) / per_page))
    current_event: Event = await Event.get_one(session, Event.current == True)  # noqa
    if current_event:
        current_event_id = current_event.id
    else:
        current_event_id = 0
    if page is None:
        page = math.floor((current_event_id - 1) / per_page)
        if page < 0:
            page = 0
    events = await Event.get_range(
        session, (page * per_page), (page * per_page) + per_page, Event.id
    )
    text = ""
    for event in events:
        entry = ""
        if event.participant:
            entry = f"<b>{event.id}.</b> {event.participant.title}"
        if event.id == current_event_id:
            entry = f"""<b>👉 {entry}</b>"""
        text = text + entry + "\n"
    menu = Menu()
    menu.formatting = False
    menu.title = f"<b>📅 Расписание</b> (страница {page + 1} из {total_pages + 1})"
    menu.text = text
    menu.keyboard = keyboard(page, total_pages, show_back_button)
    await menu.show(message)


def keyboard(page, total_pages: int, show_back_button: bool = False):
    navigation_buttons = []
    if page > 0:
        navigation_buttons.insert(
            0,
            types.InlineKeyboardButton(
                text="⏪", callback_data=ShowSchedule(page=0).pack()
            ),
        )
        navigation_buttons.insert(
            1,
            types.InlineKeyboardButton(
                text="◀️", callback_data=ShowSchedule(page=page - 1).pack()
            ),
        )
    else:
        navigation_buttons.insert(
            0, types.InlineKeyboardButton(text="⠀", callback_data="dummy")
        )
        navigation_buttons.insert(
            1, types.InlineKeyboardButton(text="⠀", callback_data="dummy")
        )
    navigation_buttons.append(
        types.InlineKeyboardButton(text="🔃", callback_data=ShowSchedule().pack())
    )
    if page < total_pages:
        navigation_buttons.append(
            types.InlineKeyboardButton(
                text="▶️", callback_data=ShowSchedule(page=page + 1).pack()
            )
        )
        navigation_buttons.append(
            types.InlineKeyboardButton(
                text="⏭️", callback_data=ShowSchedule(page=total_pages).pack()
            )
        )
    else:
        navigation_buttons.append(
            types.InlineKeyboardButton(text="⠀", callback_data="dummy")
        )
        navigation_buttons.append(
            types.InlineKeyboardButton(text="⠀", callback_data="dummy")
        )
    buttons = [navigation_buttons]
    if show_back_button:
        buttons.append(
            [
                types.InlineKeyboardButton(
                    text=strings.buttons.back,
                    callback_data=OpenMenu(menu="main").pack(),
                )
            ]
        )
    kb = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return kb
