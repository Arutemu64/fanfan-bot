from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery

from fanfan.application.dto.callback import DeleteDeliveryCallback
from fanfan.infrastructure.scheduler.utils.notifications import delete_delivery

router = Router(name="callbacks_router")


@router.callback_query(F.data == "delete")
async def delete_message(callback: CallbackQuery):
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        await callback.answer("⚠️ Этому сообщению больше 2 дней, удалите его вручную")


@router.callback_query(DeleteDeliveryCallback.filter())
async def delete_delivery_callback(
    query: CallbackQuery,
    callback_data: DeleteDeliveryCallback,
):
    delivery_info = await delete_delivery(delivery_id=callback_data.delivery_id)
    await query.answer(
        text=f"✅ Будет удалено {delivery_info.count} уведомлений",
        show_alert=True,
    )
