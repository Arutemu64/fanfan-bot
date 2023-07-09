from aiogram import Router, types

from bot.handlers.cb_factories import ShowActivity
from bot.ui import menus

router = Router(name="activities_router")


@router.callback_query(ShowActivity.filter())
async def open_activities_menu(
    callback: types.CallbackQuery, callback_data: ShowActivity
):
    await menus.activities.show(callback.message, callback_data.id)
    await callback.answer()
