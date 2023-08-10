from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from sqlalchemy import or_

from src.bot.ui import strings
from src.db import Database
from src.db.models import User

router = Router(name="org_router")


@router.message(Command("role"), flags={"allowed_roles": ["org"]})
async def vote(message: Message, command: CommandObject, db: Database):
    if not command.args:
        await message.reply(strings.errors.wrong_command_usage)
        return
    args = command.args.split()
    if not args[1] in {"visitor", "helper", "org"}:
        await message.reply(strings.errors.wrong_command_usage)
        return
    username = args[0].replace("@", "").lower()
    user = await db.user.get_by_where(User.username == username)
    if user is None:
        return
    user.role = args[1]
    await db.session.commit()


@router.message(Command("info"))
async def get_user_info(message: Message, command: CommandObject, db: Database):
    if not command.args:
        await message.reply(strings.errors.wrong_command_usage)
        return
    query = command.args.replace("@", "")
    if type(query) is not str:
        await message.reply(strings.errors.wrong_command_usage)
        return
    stmt = or_(User.ticket_id == query, User.username == query)
    if query.isnumeric():
        stmt = or_(stmt, User.id == int(query))
    user = await db.user.get_by_where(stmt)
    if user:
        info = f"<i>👤 Пользователь найден</i>\n\nid: {user.id}\nusername: {user.username}\nrole: {user.role}"
        await message.reply(text=info)
    else:
        await message.reply("Такой пользователь не найден")
