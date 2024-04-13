from aiogram.types import InlineKeyboardButton

from fanfan.application.dto.callback import DeleteDeliveryCallback

DELETE_BUTTON = InlineKeyboardButton(text="👀 Прочитано", callback_data="delete")


def get_delete_delivery_button(delivery_id: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text="🗑️ Отменить рассылку",
        callback_data=DeleteDeliveryCallback(delivery_id=delivery_id).pack(),
    )
