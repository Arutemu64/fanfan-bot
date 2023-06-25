import random
from bot.ui import keyboards, strings

from aiogram.types import Message

from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models import Vote, User, Settings, Nomination
from bot.db import requests


async def main_menu(message: Message, user: User):
    first_name = message.chat.first_name
    random_quote = random.choice(strings.quotes)
    kb = keyboards.main_menu_kb(user.role, user.notifications_enabled)
    text = strings.main_menu_text(first_name, random_quote)
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
    performances = await requests.fetch_performances(session, nomination_id=nomination_id)
    results = await requests.fetch_nominations(session, nomination_id=nomination_id)
    nomination: Nomination = results.one_or_none()
    results = await requests.fetch_votes(session, tg_id=message.chat.id, nomination_id=nomination_id)
    user_vote: Vote = results.one_or_none()

    performances_list = ''
    for performance in performances:
        entry = '<b>' + str(performance.position) + '</b>. ' + performance.name + " " + \
                "<b>[" + str(await requests.how_many_votes(session, performance.position)) + " голосов]</b>" + '\n'
        if user_vote is not None:
            if user_vote.position == performance.position:
                entry = "<b>✅ " + entry + "</b>"
        performances_list = performances_list + entry
    text = f"""<b>Номинация {nomination.name}</b>
В этой номинации представлены следующие участники:
{performances_list}
Чтобы проголосовать, используй команду <code>/vote [номер участника]</code>.
Отменить голос можно командой <code>/unvote [номер участника]</code>"""
    kb = keyboards.voting_menu_kb()
    await message.edit_text(text, reply_markup=kb)
