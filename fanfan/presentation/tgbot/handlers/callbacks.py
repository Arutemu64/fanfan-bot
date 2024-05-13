from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery

from fanfan.application.dto.callback import DeleteDeliveryCallback
from fanfan.application.exceptions import ServiceError
from fanfan.application.holder import AppHolder

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
    app: AppHolder,
):
    try:
        delivery_info = await app.notifications.delete_delivery(
            delivery_id=callback_data.delivery_id
        )
        await query.answer(
            text=f"✅ Будет удалено {delivery_info.count} уведомлений",
            show_alert=True,
        )
    except ServiceError as e:
        await query.answer(
            text=e.message,
            show_alert=True,
        )
        await query.answer()
