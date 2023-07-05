from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models import Event, Vote
from bot.ui import strings

router = Router(name='voting_router')


@router.message(Command("vote"))
async def vote(message: Message, command: CommandObject, session: AsyncSession):
    if not command.args:
        await message.reply(strings.errors.wrong_command_usage)
        return
    params = command.args.split()
    if not params[0].isnumeric():
        await message.reply(strings.errors.wrong_command_usage)
        return
    event_id = int(params[0])
    performance = await Event.get_one(session, Event.id == event_id)
    if not performance:
        await message.reply(strings.errors.performance_doesnt_exist)
        return 0
    check_vote = await Vote.get_one(session, and_(Vote.tg_id == message.from_user.id,
                                                  Vote.nomination_id == performance.nomination_id))
    if check_vote:
        await message.reply(strings.errors.already_voted)
        return 0
    new_vote = Vote(tg_id=message.from_user.id, event_id=event_id, nomination_id=performance.nomination_id)
    session.add(new_vote)
    await session.commit()
    await message.reply(strings.success.voted_successfully)


@router.message(Command("unvote"))
async def vote(message: Message, command: CommandObject, session: AsyncSession):
    if not command.args:
        await message.reply(strings.errors.wrong_command_usage)
        return
    params = command.args.split()
    if not params[0].isnumeric():
        await message.reply(strings.errors.wrong_command_usage)
        return
    event_id = int(params[0])
    performance = await Event.get_one(session, Event.id == event_id)
    if performance is None:
        await message.reply(strings.errors.performance_doesnt_exist)
        return
    user_vote = await Vote.get_one(session, and_(Vote.tg_id == message.from_user.id,
                                                 Vote.event_id == event_id))
    if user_vote:
        await session.delete(user_vote)
        await session.commit()
        await message.reply(strings.success.unvoted)
    else:
        await message.reply(strings.errors.not_voted)
