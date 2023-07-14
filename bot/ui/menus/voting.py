from aiogram import types
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models import Nomination, Participant, Vote
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


async def show_voting(session: AsyncSession, message: Message, nomination_id: str):
    participants_list = ""
    nomination = await Nomination.get_one(session, Nomination.id == nomination_id)
    user_vote = await Vote.get_one(
        session,
        and_(Vote.tg_id == message.chat.id, Vote.nomination_id == nomination_id),
    )
    for participant in nomination.participants:
        participant: Participant
        entry = f"<b>{str(participant.id)}.</b> {participant.title} [голосов: {len(participant.votes)}]\n"
        if user_vote is not None:
            if user_vote.participant_id == participant.id:
                entry = f"✅ <b>{entry}</b>"
        participants_list = participants_list + entry
    menu = Menu()
    menu.title = f"📊 Номинация {nomination.title}"
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
                text=nomination.title,
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
