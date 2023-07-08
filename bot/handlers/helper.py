from aiogram import types, Router
from magic_filter import F

from bot.handlers.cb_factories import OpenMenu

from bot.ui import menus

router = Router(name='helper_router')


@router.callback_query(OpenMenu.filter(F.menu == 'helper'), flags={'allowed_roles': ['helper', 'org']})
async def open_helper_menu(callback: types.CallbackQuery):
    await menus.helper.show(callback.message)
    await callback.answer()
