import typing

from aiogram.types import Message
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.input import ManagedTextInput, TextInput
from aiogram_dialog.widgets.kbd import SwitchTo
from aiogram_dialog.widgets.text import Const, Jinja

from fanfan.application.marketplace.update_product import UpdateProduct
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.marketplace.common import (
    DATA_SELECTED_PRODUCT_ID,
)
from fanfan.presentation.tgbot.dialogs.marketplace.product.common import product_getter
from fanfan.presentation.tgbot.static import strings

if typing.TYPE_CHECKING:
    from dishka import AsyncContainer


async def edit_product_price_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: float,
) -> None:
    container: AsyncContainer = dialog_manager.middleware_data["container"]
    update_product: UpdateProduct = await container.get(UpdateProduct)

    await update_product.update_product_price(
        product_id=dialog_manager.dialog_data[DATA_SELECTED_PRODUCT_ID], new_price=data
    )

    await dialog_manager.switch_to(state=states.Marketplace.VIEW_PRODUCT)


edit_product_price_window = Window(
    Const("💸 Укажите цену товара в рублях (целое/дробное число)"),
    Const(" "),
    Jinja("Текущая цена: <code>{{ product_price }}</code> ₽"),
    TextInput(
        id="product_price_input",
        type_factory=float,
        on_success=edit_product_price_handler,
    ),
    SwitchTo(
        Const(strings.buttons.back), state=states.Marketplace.VIEW_PRODUCT, id="back"
    ),
    state=states.Marketplace.EDIT_PRODUCT_PRICE,
    getter=product_getter,
)
