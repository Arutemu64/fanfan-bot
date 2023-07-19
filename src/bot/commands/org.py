from aiogram import Bot, Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from sqlalchemy import or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot import utils
from src.bot.ui import strings
from src.db.models import User

router = Router(name="org_router")


@router.message(Command("role"), flags={"allowed_roles": ["org"]})
async def vote(
    message: Message, command: CommandObject, session: AsyncSession, bot: Bot
):
    if not command.args:
        await message.reply(strings.errors.wrong_command_usage)
        return
    args = command.args.split()
    if not args[1] in {"visitor", "helper", "org"}:
        await message.reply(strings.errors.wrong_command_usage)
        return
    username = args[0].replace("@", "").lower()
    user = await User.get_one(session, User.username == username)
    if user is None:
        return
    user.role = args[1]
    await session.commit()
    text = f"@{message.from_user.username} ({message.from_user.id}) изменил роль пользователя @{username} ({user.tg_id}) на {args[1]}"
    await utils.service_message(session, bot, text)


@router.message(Command("info"))
async def get_user_info(
    message: Message, command: CommandObject, session: AsyncSession
):
    if not command.args:
        await message.reply(strings.errors.wrong_command_usage)
        return
    query = command.args.replace("@", "")
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
