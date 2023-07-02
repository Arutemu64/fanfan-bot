from aiogram import types, Router
from aiogram.filters import Text, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.db.models import User
from bot.handlers.auth import auth
from bot.ui import strings

router = Router(name='common_router')


@router.message(Command("start"))  # /start - выводит приветствие и производит авторизацию пользователя
async def start_cmd(message: Message, state: FSMContext, user: User):
    await message.reply(strings.common.welcome)
    await auth(message, state, user)


@router.message(Command("menu"))  # /menu - как /start, только без приветствия
async def menu_cmd(message: Message, state: FSMContext, user: User):
    await auth(message, state, user)


@router.callback_query(Text("delete_message"))
async def delete_message(callback: types.CallbackQuery):
    await callback.message.delete()
    await callback.answer()


@router.callback_query(Text("dummy"))
async def dummy(callback: types.CallbackQuery):
    await callback.answer()
