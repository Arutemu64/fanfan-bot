from aiogram import Router, types
from aiogram.filters import Text
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from bot.handlers.announce import Modes
from bot.ui import menus

router = Router(name='schedule_router')


@router.callback_query(Text(startswith="open_schedule_page"))
async def switch_schedule_page(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    page = None
    if len(callback.data.split()) > 1:
        page = int(callback.data.split()[1])
    show_back_button = (await state.get_state()) != Modes.AnnounceMode
    await menus.schedule.show(session,
                              message=callback.message,
                              page=page,
                              show_back_button=show_back_button)
    await callback.answer()


@router.callback_query(Text(startswith="update_schedule"))
async def update_schedule_page(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    show_back_button = (await state.get_state()) != Modes.AnnounceMode
    await menus.schedule.show(session,
                              message=callback.message,
                              show_back_button=show_back_button)
    await callback.answer()
