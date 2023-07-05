import math

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession

from bot.config import conf
from bot.db.models import Vote, User, Settings, Nomination, Event
from bot.ui import keyboards, strings


async def main_menu(message: Message, user: User):
    kb = keyboards.main_menu_kb(user.role)
    text = strings.menus.main_menu_text(first_name=message.chat.first_name)
    await message.edit_text(text, reply_markup=kb)


async def nominations_menu(message: Message, session: AsyncSession):
    nominations = await Nomination.get_many(session, True)
    text = f"""<b>Голосование</b>\nДля голосования доступны следующие номинации:"""
    kb = keyboards.nominations_menu_kb(nominations)
    await message.edit_text(text, reply_markup=kb)


async def helper_menu(message):
    text = strings.menus.helper_menu_text
    kb = keyboards.helper_menu_kb()
    await message.edit_text(text, reply_markup=kb)


async def org_menu(message, settings: Settings):
    text = strings.menus.org_menu_text
    kb = keyboards.org_menu_kb(settings)
    await message.edit_text(text, reply_markup=kb)


async def voting_menu(session: AsyncSession, message, nomination_id: int):
    performances = await Event.get_many(session, Event.nomination_id == nomination_id)
    nomination = await Nomination.get_one(session, Nomination.id == nomination_id)
    user_vote = await Vote.get_one(session, and_(Vote.tg_id == message.chat.id,
                                                 Vote.nomination_id == nomination_id))
    performances_list = ''
    for performance in performances:
        votes_count = await Vote.count(session, Vote.event_id == performance.id)
        entry = f"<b>{str(performance.id)}.</b> {performance.title} [голосов: {votes_count}]\n"
        if user_vote is not None:
            if user_vote.event_id == performance.id:
                entry = f"✅ <b>{entry}</b>"
        performances_list = performances_list + entry
    text = f"""<b>Номинация {nomination.name}</b>
В этой номинации представлены следующие участники:
{performances_list}
Чтобы проголосовать, используй команду <code>/vote номер_участника</code>.
Отменить голос можно командой <code>/unvote номер_участника</code>"""
    kb = keyboards.voting_menu_kb()
    await message.edit_text(text, reply_markup=kb)


async def schedule_menu(session: AsyncSession, message, show_back_button: bool = False, page: int = None):
    settings = await Settings.get_one(session, True)
    per_page = conf.events_per_page
    if page is None:
        page = math.floor((settings.current_event_id - 1) / per_page)
        if page == 0:
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
    kb = keyboards.schedule_menu_kb(page, total_pages, show_back_button)
    try:
        await message.edit_text(text, reply_markup=kb)
    except TelegramBadRequest:
        return
