import typing

from aiogram.types import Message
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.input import ManagedTextInput, TextInput
from aiogram_dialog.widgets.kbd import SwitchTo
from aiogram_dialog.widgets.text import Const, Jinja

from fanfan.application.marketplace.update_product import UpdateProduct
from fanfan.core.models.product import MAX_PRODUCT_NAME_LENGTH
from fanfan.core.vo.product import ProductId
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.marketplace.common import (
    DATA_SELECTED_PRODUCT_ID,
)
from fanfan.presentation.tgbot.dialogs.marketplace.product.common import product_getter
from fanfan.presentation.tgbot.static import strings

if typing.TYPE_CHECKING:
    from dishka import AsyncContainer


async def edit_product_name_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: str,
) -> None:
    container: AsyncContainer = dialog_manager.middleware_data["container"]
    update_product: UpdateProduct = await container.get(UpdateProduct)

    await update_product.update_product_name(
        product_id=ProductId(dialog_manager.dialog_data[DATA_SELECTED_PRODUCT_ID]),
        new_name=data,
    )

    await dialog_manager.switch_to(state=states.Marketplace.VIEW_PRODUCT)


edit_product_name_window = Window(
    Const(
        f"⌨️ Отправьте новое название товара "
        f"(не более {MAX_PRODUCT_NAME_LENGTH} символов)"
    ),
    Const(" "),
    Jinja("Текущее название: <code>{{ product_name }}</code>"),
    TextInput(id="product_name_input", on_success=edit_product_name_handler),
    SwitchTo(
        Const(strings.buttons.back), state=states.Marketplace.VIEW_PRODUCT, id="back"
    ),
    state=states.Marketplace.EDIT_PRODUCT_NAME,
    getter=product_getter,
)
