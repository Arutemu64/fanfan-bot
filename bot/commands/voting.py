from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models import Participant, Settings, Vote
from bot.ui import strings

router = Router(name="voting_router")


@router.message(Command("vote"))
async def vote(message: Message, command: CommandObject, session: AsyncSession):
    settings = await Settings.get_one(session, True)
    if not settings.voting_enabled:
        await message.reply(strings.errors.voting_disabled)
        return
    if not command.args:
        await message.reply(strings.errors.wrong_command_usage)
        return
    params = command.args.split()
    if not params[0].isnumeric():
        await message.reply(strings.errors.wrong_command_usage)
        return
    participant_id = int(params[0])
    participant = await Participant.get_one(session, Participant.id == participant_id)
    if not participant:
        await message.reply(strings.errors.performance_doesnt_exist)
        return 0
    check_vote = await Vote.get_one(
        session,
        and_(
            Vote.tg_id == message.from_user.id,
            Vote.participant.has(
                Participant.nomination_id == participant.nomination_id
            ),
        ),
    )
    if check_vote:
        await message.reply(strings.errors.already_voted)
        return 0
    new_vote = Vote()
    new_vote.tg_id = message.from_user.id
    new_vote.participant_id = participant.id
    session.add(new_vote)
    await session.commit()
    await message.reply(strings.success.voted_successfully)


@router.message(Command("unvote"))
async def vote(message: Message, command: CommandObject, session: AsyncSession):
    settings = await Settings.get_one(session, True)
    if not settings.voting_enabled:
        await message.reply(strings.errors.voting_disabled)
        return
    if not command.args:
        await message.reply(strings.errors.wrong_command_usage)
        return
    params = command.args.split()
    if not params[0].isnumeric():
        await message.reply(strings.errors.wrong_command_usage)
        return
    participant_id = int(params[0])
    participant = await Participant.get_one(session, Participant.id == participant_id)
    if participant is None:
        await message.reply(strings.errors.performance_doesnt_exist)
        return
    user_vote = await Vote.get_one(
        session,
        and_(
            Vote.tg_id == message.from_user.id,
            Vote.participant.has(Participant.id == participant.id),
        ),
    )
    if user_vote:
        await session.delete(user_vote)
        await session.commit()
        await message.reply(strings.success.unvoted)
    else:
        await message.reply(strings.errors.not_voted)
