from aiogram.enums import ContentType
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, SwitchTo
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.text import Const
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from fanfan.application.marketplace.update_product import UpdateProduct
from fanfan.core.vo.telegram import TelegramFileId
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.utils import get_dialog_data_adapter
from fanfan.presentation.tgbot.dialogs.marketplace.data import (
    MarketDialogData,
)
from fanfan.presentation.tgbot.dialogs.marketplace.product.common import product_getter
from fanfan.presentation.tgbot.static import strings


@inject
async def new_product_image_handler(
    message: Message,
    message_input: MessageInput,
    manager: DialogManager,
    update_product: FromDishka[UpdateProduct],
):
    dialog_data_adapter = get_dialog_data_adapter(manager)
    dialog_data = dialog_data_adapter.load(MarketDialogData)
    if message.photo:
        await update_product.update_product_image(
            product_id=dialog_data.product_id,
            new_image_id=TelegramFileId(message.photo[-1].file_id),
        )


@inject
async def delete_image_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
    update_product: FromDishka[UpdateProduct],
):
    dialog_data_adapter = get_dialog_data_adapter(manager)
    dialog_data = dialog_data_adapter.load(MarketDialogData)
    await update_product.update_product_image(
        product_id=dialog_data.product_id,
        new_image_id=None,
    )


edit_product_image_window = Window(
    DynamicMedia(
        selector="product_image",
        when="product_image",
    ),
    Const("🖼️ Отправьте новое изображение сообщением"),
    MessageInput(new_product_image_handler, content_types=[ContentType.PHOTO]),
    Button(
        Const("🗑️ Удалить изображение"),
        id="delete_product_image",
        when="product_image",
        on_click=delete_image_handler,
    ),
    SwitchTo(
        Const(strings.buttons.back), state=states.Marketplace.VIEW_PRODUCT, id="back"
    ),
    state=states.Marketplace.EDIT_PRODUCT_IMAGE,
    getter=product_getter,
)
