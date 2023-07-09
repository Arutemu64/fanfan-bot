from aiogram import Router, types
from aiogram.filters import Command, Text
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from magic_filter import F

from bot.db.models import User
from bot.handlers.auth import auth
from bot.handlers.cb_factories import OpenMenu
from bot.ui import menus, strings

router = Router(name="common_router")


@router.message(Command("start"), flags={"bypass_verification": True})
async def start_cmd(message: Message, state: FSMContext, user: User):
    await message.reply(strings.common.welcome)
    await auth(message, state, user)


@router.message(Command("menu"), flags={"bypass_verification": True})
async def menu_cmd(message: Message, state: FSMContext, user: User):
    await auth(message, state, user)


@router.callback_query(OpenMenu.filter(F.menu == "main"))
async def open_main_menu(callback: types.CallbackQuery, user: User):
    await menus.main.show(callback.message, user)
    await callback.answer()


@router.callback_query(Text("delete_message"))
async def delete_message(callback: types.CallbackQuery):
    await callback.message.delete()
    await callback.answer()


@router.callback_query(Text("dummy"))
async def dummy(callback: types.CallbackQuery):
    await callback.answer()
