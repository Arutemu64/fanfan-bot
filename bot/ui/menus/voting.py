from aiogram import types
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models import Event, Nomination, Vote
from bot.handlers.cb_factories import OpenMenu, ShowNomination
from bot.models import Menu
from bot.ui import strings


async def show_nominations(message: Message, session: AsyncSession):
    nominations = await Nomination.get_many(session, True)
    menu = Menu()
    menu.title = "📊 Голосование"
    menu.text = "Для голосования доступны следующие номинации:"
    menu.keyboard = nominations_kb(nominations)
    await menu.show(message)


async def show_voting(session: AsyncSession, message, nomination_id: int):
    participants_list = await get_list(session, message.chat.id, nomination_id)
    nomination = await Nomination.get_one(session, Nomination.id == nomination_id)
    menu = Menu()
    menu.title = f"📊 Номинация {nomination.name}"
    menu.text = f"""В этой номинации представлены следующие участники:
{participants_list}
Чтобы проголосовать, используй команду <code>/vote номер_участника</code>.
Отменить голос можно командой <code>/unvote номер_участника</code>"""
    menu.keyboard = voting_kb()
    await menu.show(message)


def nominations_kb(nominations):
    builder = InlineKeyboardBuilder()
    for nomination in nominations:
        builder.row(
            types.InlineKeyboardButton(
                text=nomination.name,
                callback_data=ShowNomination(id=nomination.id).pack(),
            )
        )
    builder.row(
        types.InlineKeyboardButton(
            text=strings.buttons.back, callback_data=OpenMenu(menu="main").pack()
        )
    )
    return builder.as_markup()


def voting_kb():
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(
            text=strings.buttons.back, callback_data=OpenMenu(menu="nominations").pack()
        )
    )
    return builder.as_markup()


async def get_list(session: AsyncSession, user_id: int, nomination_id: int):
    performances = await Event.get_many(session, Event.nomination_id == nomination_id)
    user_vote = await Vote.get_one(
        session,
        and_(Vote.tg_id == user_id, Vote.nomination_id == nomination_id),
    )
    performances_list = ""
    for performance in performances:
        votes_count = await Vote.count(session, Vote.event_id == performance.id)
        entry = f"<b>{str(performance.id)}.</b> {performance.title} [голосов: {votes_count}]\n"
        if user_vote is not None:
            if user_vote.event_id == performance.id:
                entry = f"✅ <b>{entry}</b>"
        performances_list = performances_list + entry
    return performances_list
