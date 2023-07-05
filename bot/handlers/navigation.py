from aiogram import types, Router
from aiogram.filters import Text
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models import User, Settings
from bot.handlers.announce import Modes
from bot.ui import menus, strings, keyboards

router = Router(name='menu_router')


@router.callback_query(Text("open_main_menu"))
async def open_main_menu(callback: types.CallbackQuery, user: User):
    await menus.main_menu(callback.message, user)
    await callback.answer()


@router.callback_query(Text("open_nominations_menu"))
async def open_nominations_menu(callback: types.CallbackQuery, session: AsyncSession):
    # settings: Settings = await requests.fetch_settings(session)
    settings = await Settings.get_one(session, True)
    if settings.voting_enabled:
        await menus.nominations_menu(callback.message, session)
        await callback.answer()
    else:
        await callback.answer(strings.errors.voting_disabled, show_alert=True)


@router.callback_query(Text("open_helper_menu"), flags={'allowed_roles': ['helper', 'org']})
async def open_helper_menu(callback: types.CallbackQuery):
    await menus.helper_menu(callback.message)
    await callback.answer()


@router.callback_query(Text("open_org_menu"), flags={'allowed_roles': ['org']})
async def open_org_menu(callback: types.CallbackQuery, session: AsyncSession):
    # settings = await requests.fetch_settings(session)
    settings = await Settings.get_one(session, True)
    await menus.org_menu(callback.message, settings)
    await callback.answer()


@router.callback_query(Text(startswith="nomination"))
async def open_voting_menu(callback: types.CallbackQuery, session: AsyncSession):
    nomination = callback.data.split()[1]
    await menus.voting_menu(session, callback.message, int(nomination))
    await callback.answer()


@router.callback_query(Text("announce_mode"), flags={'allowed_roles': ['helper', 'org']})
async def announce_mode(callback: types.CallbackQuery, state: FSMContext):
    kb = keyboards.announce_mode_kb()
    await callback.message.answer(text=strings.menus.announce_mode_text, reply_markup=kb)
    await state.set_state(Modes.AnnounceMode)
    await callback.answer()
