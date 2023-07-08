from aiogram import Router, types
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from magic_filter import F
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models import Event, Vote, Settings
from bot.handlers.cb_factories import ShowNomination, OpenMenu
from bot.ui import strings, menus

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


@router.callback_query(OpenMenu.filter(F.menu == 'nominations'))
async def open_nominations_menu(callback: types.CallbackQuery, session: AsyncSession):
    settings = await Settings.get_one(session, True)
    if settings.voting_enabled:
        await menus.voting.show_nominations(callback.message, session)
        await callback.answer()
    else:
        await callback.answer(strings.errors.voting_disabled, show_alert=True)


@router.callback_query(ShowNomination.filter())
async def open_voting_menu(callback: types.CallbackQuery,
                           callback_data: ShowNomination,
                           session: AsyncSession):
    await menus.voting.show_voting(session, callback.message, callback_data.id)
    await callback.answer()
