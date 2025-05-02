from aiogram.enums import ContentType
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, SwitchTo
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.text import Const
from dishka import AsyncContainer

from fanfan.application.marketplace.get_product import GetProduct
from fanfan.application.marketplace.update_product import UpdateProduct
from fanfan.core.models.product import ProductId
from fanfan.core.value_objects import TelegramFileId
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.marketplace.common import (
    DATA_SELECTED_PRODUCT_ID,
)
from fanfan.presentation.tgbot.static import strings


async def product_image_getter(
    dialog_manager: DialogManager,
    container: AsyncContainer,
    **kwargs,
):
    product_id = ProductId(dialog_manager.dialog_data[DATA_SELECTED_PRODUCT_ID])
    get_product: GetProduct = await container.get(GetProduct)
    product = await get_product(product_id=product_id)

    product_image = None
    if product.image_id:
        product_image = MediaAttachment(
            ContentType.PHOTO, file_id=MediaId(product.image_id)
        )

    return {
        "product_image": product_image,
    }


async def new_product_image_handler(
    message: Message,
    message_input: MessageInput,
    manager: DialogManager,
):
    container: AsyncContainer = manager.middleware_data["container"]
    update_product: UpdateProduct = await container.get(UpdateProduct)
    if message.photo:
        await update_product.update_product_image(
            product_id=ProductId(manager.dialog_data[DATA_SELECTED_PRODUCT_ID]),
            new_image_id=TelegramFileId(message.photo[-1].file_id),
        )


async def delete_image_handler(
    callback: CallbackQuery, button: Button, manager: DialogManager
):
    container: AsyncContainer = manager.middleware_data["container"]
    update_product: UpdateProduct = await container.get(UpdateProduct)
    await update_product.update_product_image(
        product_id=ProductId(manager.dialog_data[DATA_SELECTED_PRODUCT_ID]),
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
    getter=product_image_getter,
)
