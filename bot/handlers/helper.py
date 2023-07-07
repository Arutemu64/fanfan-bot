from aiogram import types, Router
from aiogram.filters import Text

from bot.ui import menus

router = Router(name='helper_router')


@router.callback_query(Text("open_helper_menu"), flags={'allowed_roles': ['helper', 'org']})
async def open_helper_menu(callback: types.CallbackQuery):
    await menus.helper.show(callback.message)
    await callback.answer()