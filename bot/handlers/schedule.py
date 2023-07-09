from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from bot.handlers.announce import Modes
from bot.handlers.cb_factories import ShowSchedule
from bot.ui import menus

router = Router(name="schedule_router")


@router.callback_query(ShowSchedule.filter())
async def switch_schedule_page(
    callback: types.CallbackQuery,
    callback_data: ShowSchedule,
    session: AsyncSession,
    state: FSMContext,
):
    show_back_button = (await state.get_state()) != Modes.AnnounceMode
    await menus.schedule.show(
        session,
        message=callback.message,
        page=callback_data.page,
        show_back_button=show_back_button,
    )
    await callback.answer()
