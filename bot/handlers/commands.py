from aiogram import Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from sqlalchemy.ext.asyncio import AsyncSession

from bot.db import requests
from bot.db.models import User, Performance, Vote

from bot.handlers import states
from bot.ui import menus, strings

from bot import utils

router = Router(name='commands_router')


async def auth(message, state, user):  # TODO принимать юзера вместо session чтобы не делать повторные запросы
    if user:
        await menus.main_menu(await message.answer(strings.loading), user)
    else:
        await message.reply(strings.please_send_ticket)
        await state.set_state(states.Registration.NotRegistered)


@router.message(Command("start"))  # /start - выводит приветствие и производит авторизацию пользователя
async def start_cmd(message: Message, state: FSMContext, user: User):
    await message.reply(strings.welcome)
    await auth(message, state, user)


@router.message(Command("menu"))  # /menu - как /start, только без приветствия
async def menu_cmd(message: Message, state: FSMContext, user: User):
    await auth(message, state, user)


@router.message(Command("vote"))
async def vote(message: Message, command: CommandObject, session: AsyncSession):
    if not command.args:
        await message.reply(strings.wrong_command_usage)
        return
    params = command.args.split()
    if not params[0].isnumeric():
        await message.reply(strings.wrong_command_usage)
        return
    position = int(params[0])
    results = await requests.fetch_performances(session, position=position)
    performance: Performance = results.one_or_none()
    if not performance:
        await message.reply(strings.performance_doesnt_exist)
        return 0
    results = await requests.fetch_votes(session, tg_id=message.from_user.id, nomination_id=performance.nomination_id)
    if results.one_or_none():
        await message.reply(strings.already_voted)
        return 0
    new_vote = Vote(tg_id=message.from_user.id, position=position, nomination_id=performance.nomination_id)
    session.add(new_vote)
    await session.commit()
    await message.reply(strings.voted_successfully)


@router.message(Command("unvote"))
async def vote(message: Message, command: CommandObject, session: AsyncSession):
    if not command.args:
        await message.reply(strings.wrong_command_usage)
        return
    params = command.args.split()
    if not params[0].isnumeric():
        await message.reply(strings.wrong_command_usage)
        return
    position = int(params[0])
    results = await requests.fetch_performances(session, position=position)
    performance: Performance = results.one_or_none()
    if performance is None:
        await message.reply(strings.performance_doesnt_exist)
        return
    results = await requests.fetch_votes(session, tg_id=message.from_user.id, position=position)
    user_vote: Vote = results.one_or_none()
    if user_vote:
        await session.delete(user_vote)
        await session.commit()
        await message.reply(strings.unvoted)
    else:
        await message.reply(strings.not_voted)


@router.message(Command("role"), flags={'allowed_roles': ['org']})
async def vote(message: Message, command: CommandObject, session: AsyncSession, bot: Bot):
    if not command.args:
        await message.reply(strings.wrong_command_usage)
        return
    args = command.args.split()
    print(args[1])
    if not args[1] in {'visitor', 'helper', 'org'}:
        await message.reply(strings.wrong_command_usage)
        return
    username = args[0].replace('@', '').lower()
    results = await requests.fetch_users(session, username=username)
    user: User = results.one_or_none()
    if user is None:
        return
    user.role = args[1]
    await session.commit()
    text = f"@{message.from_user.username} ({message.from_user.id}) изменил роль пользователя @{username} ({user.tg_id}) на {args[1]}"
    await utils.service_message(session, bot, text)

