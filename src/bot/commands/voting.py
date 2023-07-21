from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from sqlalchemy import and_

from src.bot.ui import strings
from src.db import Database
from src.db.models import Participant, Vote

router = Router(name="voting_router")


@router.message(Command("vote"))
async def vote(message: Message, command: CommandObject, db: Database):
    settings = await db.settings.get_by_where(True)
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
    participant = await db.participant.get_by_where(Participant.id == participant_id)
    if not participant:
        await message.reply(strings.errors.performance_doesnt_exist)
        return 0
    check_vote = await db.vote.get_by_where(
        and_(
            Vote.tg_id == message.from_user.id,
            Vote.participant.has(
                Participant.nomination_id == participant.nomination_id
            ),
        )
    )
    if check_vote:
        await message.reply(strings.errors.already_voted)
        return 0
    await db.vote.new(message.from_user.id, participant.id)
    await db.session.commit()
    await message.reply(strings.success.voted_successfully)


@router.message(Command("unvote"))
async def vote(message: Message, command: CommandObject, db: Database):
    settings = await db.settings.get_by_where(True)
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
    participant = await db.participant.get_by_where(Participant.id == participant_id)
    if participant is None:
        await message.reply(strings.errors.performance_doesnt_exist)
        return
    user_vote = await db.vote.get_by_where(
        and_(
            Vote.tg_id == message.from_user.id,
            Vote.participant.has(Participant.id == participant.id),
        )
    )
    if user_vote:
        await db.session.delete(user_vote)
        await db.session.commit()
        await message.reply(strings.success.unvoted)
    else:
        await message.reply(strings.errors.not_voted)
