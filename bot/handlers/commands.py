from aiogram import Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from sqlalchemy.ext.asyncio import AsyncSession

from bot.db import requests
from bot.db.models import User, Event, Vote

from bot.handlers import states
from bot.ui import menus, strings

from bot import utils

from sqlalchemy import or_, and_

router = Router(name='commands_router')


async def auth(message, state, user):
    await state.clear()
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
    event_id = int(params[0])
    performance: Event = await requests.get_event(session, Event.id == event_id)
    if not performance:
        await message.reply(strings.performance_doesnt_exist)
        return 0
    # results = await requests.fetch_votes(session, tg_id=message.from_user.id, nomination_id=performance.nomination_id)
    vote: Vote = await requests.get_vote(session, and_(Vote.tg_id == message.from_user.id,
                                                       Vote.nomination_id == performance.nomination_id))
    if vote:
        await message.reply(strings.already_voted)
        return 0
    new_vote = Vote(tg_id=message.from_user.id, event_id=event_id, nomination_id=performance.nomination_id)
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
    event_id = int(params[0])
    performance: Event = await requests.get_event(session, Event.id == event_id)
    if performance is None:
        await message.reply(strings.performance_doesnt_exist)
        return
    user_vote: Vote = await requests.get_vote(session, and_(Vote.tg_id == message.from_user.id,
                                                            Vote.event_id == event_id))
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
    if not args[1] in {'visitor', 'helper', 'org'}:
        await message.reply(strings.wrong_command_usage)
        return
    username = args[0].replace('@', '').lower()
    user: User = await requests.get_user(session, User.username == username)
    if user is None:
        return
    user.role = args[1]
    await session.commit()
    text = f"@{message.from_user.username} ({message.from_user.id}) изменил роль пользователя @{username} ({user.tg_id}) на {args[1]}"
    await utils.service_message(session, bot, text)


# @router.message(Command("msg"), flags={'allowed_roles': ['org']})
# async def msg(message: Message, command: CommandObject, session: AsyncSession, bot: Bot):
#     if not command.args:
#         await message.reply(strings.wrong_command_usage)
#         return
#     args = command.args.split(" ", 1)
#     if not args[0] in {'helper', 'org'}:
#         await message.reply(strings.wrong_command_usage)
#         return
#     group = ''
#     users = await requests.get_users(session, and_(User.role == 'org', User.tg_id is not None))
#     if args[0] == "helper":
#         group = "Сообщение для волонтёров"
#         helpers = await requests.get_users(session, and_(User.role == 'helper', User.tg_id is not None))
#         users = users + helpers
#     elif args[0] == "org":
#         group = "Сообщение для организаторов"
#     text = f"<i>💬 {group}</i>\n\n{args[1]}\n\n<i>Отправил @{message.from_user.username} ({message.from_user.id})</i>"
#     for user in users:
#         await bot.send_message(text=text, chat_id=user.tg_id)


@router.message(Command("info"), flags={'allowed_roles': ['org']})
async def get_user_info(message: Message, command: CommandObject, session: AsyncSession):
    if not command.args:
        await message.reply(strings.wrong_command_usage)
        return
    query = command.args.replace('@', '')
    if type(query) is not str:
        await message.reply(strings.wrong_command_usage)
        return
    stmt = or_(User.ticket_id == query, User.username == query)
    if query.isnumeric():
        stmt = or_(stmt, User.tg_id == int(query))
    user = await requests.get_user(session, stmt)
    if user:
        info = f"<i>👤 Пользователь найден</i>\n\nticket_id: {user.ticket_id}\ntg_id: {user.tg_id}\nusername: {user.username}\nrole: {user.role}"
        await message.reply(text=info)
    else:
        await message.reply("Такой пользователь не найден")
