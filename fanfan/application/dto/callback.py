from aiogram.filters.callback_data import CallbackData


class DeleteDeliveryCallback(CallbackData, prefix="delete_delivery"):
    delivery_id: str
