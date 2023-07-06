from aiogram import types, Router
from aiogram.filters import Text
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models import User, Settings
from bot.handlers.announce import Modes
from bot.ui import menus, strings

router = Router(name='menu_router')


@router.callback_query(Text("open_main_menu"))
async def open_main_menu(callback: types.CallbackQuery, user: User):
    await menus.main.show(callback.message, user)
    await callback.answer()


@router.callback_query(Text("open_nominations_menu"))
async def open_nominations_menu(callback: types.CallbackQuery, session: AsyncSession):
    settings = await Settings.get_one(session, True)
    if settings.voting_enabled:
        await menus.voting.show_nominations(callback.message, session)
        await callback.answer()
    else:
        await callback.answer(strings.errors.voting_disabled, show_alert=True)


@router.callback_query(Text("open_helper_menu"), flags={'allowed_roles': ['helper', 'org']})
async def open_helper_menu(callback: types.CallbackQuery):
    await menus.helper.show(callback.message)
    await callback.answer()


@router.callback_query(Text("open_org_menu"), flags={'allowed_roles': ['org']})
async def open_org_menu(callback: types.CallbackQuery, session: AsyncSession):
    settings = await Settings.get_one(session, True)
    await menus.org.show(callback.message, settings)
    await callback.answer()


@router.callback_query(Text(startswith="nomination"))
async def open_voting_menu(callback: types.CallbackQuery, session: AsyncSession):
    nomination = callback.data.split()[1]
    await menus.voting.show_voting(session, callback.message, int(nomination))
    await callback.answer()


@router.callback_query(Text("announce_mode"), flags={'allowed_roles': ['helper', 'org']})
async def announce_mode(callback: types.CallbackQuery, state: FSMContext):
    kb = await menus.announce.announce_mode_keyboard()
    await callback.message.answer(text=strings.menus.announce_mode_text, reply_markup=kb)
    await state.set_state(Modes.AnnounceMode)
    await callback.answer()
