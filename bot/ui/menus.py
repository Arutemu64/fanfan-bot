import math

from aiogram.types import Message
from aiogram.exceptions import TelegramBadRequest

from bot.ui import keyboards, strings
from bot.db.models import Vote, User, Settings, Nomination, Event
from bot.db import requests
from bot.config import conf

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_


async def main_menu(message: Message, user: User):
    first_name = message.chat.first_name
    kb = keyboards.main_menu_kb(user.role)
    text = strings.main_menu_text(first_name)
    await message.edit_text(text, reply_markup=kb)


async def nominations_menu(message: Message, session: AsyncSession):
    nominations = await requests.fetch_nominations(session)
    text = f"""<b>Голосование</b>\nДля голосования доступны следующие номинации:"""
    kb = keyboards.nominations_menu_kb(nominations)
    await message.edit_text(text, reply_markup=kb)


async def helper_menu(message):
    text = strings.helper_guide
    kb = keyboards.helper_menu_kb()
    await message.edit_text(text, reply_markup=kb)


async def org_menu(message, settings: Settings):
    text = strings.org_guide
    kb = keyboards.org_menu_kb(settings)
    await message.edit_text(text, reply_markup=kb)


async def voting_menu(session: AsyncSession, message, nomination_id: int):
    performances = await requests.get_events(session, Event.nomination_id == nomination_id)
    results = await requests.fetch_nominations(session, nomination_id=nomination_id)
    nomination: Nomination = results.one_or_none()
    user_vote: Vote = await requests.get_vote(session, and_(Vote.tg_id == message.chat.id,
                                                            Vote.nomination_id == nomination_id))
    performances_list = ''
    for performance in performances:
        votes_count = len(await requests.get_votes(session, Vote.event_id == performance.id))
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
    settings = await requests.fetch_settings(session)
    per_page = conf.events_per_page
    all_events = await requests.get_events(session, True)
    if page is None:
        page = math.floor((settings.current_event_id - 1) / per_page)
        if page < 0:
            page = 0
    events = all_events[(page * per_page):(page * per_page) + per_page]
    total_pages = math.ceil((len(all_events) - 1) / per_page)
    text = f"<b>📅 Расписание</b> (страница {page + 1} из {total_pages + 1})\n\n"
    for event in events:
        entry = ''
        if event.id:
            entry = f"<b>{event.id}.</b> {event.title}"
        # elif event.title:
        #     entry = f"<b>------{event.title}------</b>"
        if event.id == settings.current_event_id:
            entry = f"""<b>👉 {entry}</b>"""
        text = text + entry + "\n"
    kb = keyboards.schedule_menu_kb(page, total_pages, show_back_button)
    try:
        await message.edit_text(text, reply_markup=kb)
    except TelegramBadRequest:
        return
