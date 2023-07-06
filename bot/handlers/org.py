from aiogram import Router, Bot, types
from aiogram.filters import Command, CommandObject, Text
from aiogram.types import Message
from sqlalchemy import or_
from sqlalchemy.ext.asyncio import AsyncSession

from bot import utils
from bot.db.models import User, Settings
from bot.ui import strings, menus

router = Router(name='auth_router')


@router.message(Command("role"), flags={'allowed_roles': ['org']})
async def vote(message: Message, command: CommandObject, session: AsyncSession, bot: Bot):
    if not command.args:
        await message.reply(strings.errors.wrong_command_usage)
        return
    args = command.args.split()
    if not args[1] in {'visitor', 'helper', 'org'}:
        await message.reply(strings.errors.wrong_command_usage)
        return
    username = args[0].replace('@', '').lower()
    user = await User.get_one(session, User.username == username)
    if user is None:
        return
    user.role = args[1]
    await session.commit()
    text = f"@{message.from_user.username} ({message.from_user.id}) изменил роль пользователя @{username} ({user.tg_id}) на {args[1]}"
    await utils.service_message(session, bot, text)


@router.message(Command("info"), flags={'allowed_roles': ['org']})
async def get_user_info(message: Message, command: CommandObject, session: AsyncSession):
    if not command.args:
        await message.reply(strings.errors.wrong_command_usage)
        return
    query = command.args.replace('@', '')
    if type(query) is not str:
        await message.reply(strings.errors.wrong_command_usage)
        return
    stmt = or_(User.ticket_id == query, User.username == query)
    if query.isnumeric():
        stmt = or_(stmt, User.tg_id == int(query))
    user = await User.get_one(session, stmt)
    if user:
        info = f"<i>👤 Пользователь найден</i>\n\nticket_id: {user.ticket_id}\ntg_id: {user.tg_id}\nusername: {user.username}\nrole: {user.role}"
        await message.reply(text=info)
    else:
        await message.reply("Такой пользователь не найден")


@router.callback_query(Text("switch_voting"), flags={'allowed_roles': ['org']})
async def announce_mode(callback: types.CallbackQuery, session: AsyncSession):
    settings = await Settings.get_one(session, True)
    settings.voting_enabled = not settings.voting_enabled
    await session.commit()
    await callback.message.edit_reply_markup(reply_markup=menus.org.keyboard(settings))
    await callback.answer()

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
