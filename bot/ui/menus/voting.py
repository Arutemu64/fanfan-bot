from aiogram import types
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models import Nomination, Event, Vote
from bot.handlers.cb_factories import ShowNomination, OpenMenu
from bot.ui import strings


async def show_nominations(message: Message, session: AsyncSession):
    nominations = await Nomination.get_many(session, True)
    text = f"""<b>📊 Голосование</b>\n\nДля голосования доступны следующие номинации:"""
    kb = nominations_kb(nominations)
    await message.edit_text(text, reply_markup=kb)


async def show_voting(session: AsyncSession, message, nomination_id: int):
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
    text = f"""<b>📊 Номинация {nomination.name}</b>

В этой номинации представлены следующие участники:
{performances_list}
Чтобы проголосовать, используй команду <code>/vote номер_участника</code>.
Отменить голос можно командой <code>/unvote номер_участника</code>"""
    kb = voting_kb()
    await message.edit_text(text, reply_markup=kb)


def nominations_kb(nominations):
    builder = InlineKeyboardBuilder()
    for nomination in nominations:
        builder.row(types.InlineKeyboardButton(text=nomination.name,
                                               callback_data=ShowNomination(id=nomination.id).pack()))
    builder.row(types.InlineKeyboardButton(text=strings.buttons.back,
                                           callback_data=OpenMenu(menu='main').pack()))
    return builder.as_markup()


def voting_kb():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text=strings.buttons.back,
                                           callback_data=OpenMenu(menu='nominations').pack()))
    return builder.as_markup()
