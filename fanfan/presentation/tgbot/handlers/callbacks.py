from aiogram import F, Router, types
from aiogram.exceptions import TelegramBadRequest

router = Router(name="callbacks_router")


@router.callback_query(F.data == "delete")
async def delete_message(callback: types.CallbackQuery):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        await callback.answer("⚠️ Этому сообщению больше 2 дней, удалите его вручную")
