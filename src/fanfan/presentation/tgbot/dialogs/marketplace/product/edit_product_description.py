from aiogram.types import Message
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.input import ManagedTextInput, TextInput
from aiogram_dialog.widgets.kbd import SwitchTo
from aiogram_dialog.widgets.text import Const, Jinja
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from fanfan.application.marketplace.update_product import UpdateProduct
from fanfan.core.models.product import (
    MAX_PRODUCT_DESCRIPTION_LENGTH,
)
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.utils import get_dialog_data_adapter
from fanfan.presentation.tgbot.dialogs.marketplace.data import (
    MarketDialogData,
)
from fanfan.presentation.tgbot.dialogs.marketplace.product.common import product_getter
from fanfan.presentation.tgbot.static import strings


@inject
async def edit_product_description_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    update_product: FromDishka[UpdateProduct],
    data: str,
) -> None:
    dialog_data_adapter = get_dialog_data_adapter(dialog_manager)
    dialog_data = dialog_data_adapter.load(MarketDialogData)
    await update_product.update_product_description(
        product_id=dialog_data.product_id,
        new_description=data,
    )

    await dialog_manager.switch_to(state=states.Marketplace.VIEW_PRODUCT)


edit_product_description_window = Window(
    Const(
        f"⌨️ Отправьте новое описание товара "
        f"(не более {MAX_PRODUCT_DESCRIPTION_LENGTH} символов)"
    ),
    Const(" "),
    Jinja("Текущее описание: <code>{{ product_description }}</code>"),
    TextInput(id="product_desc_input", on_success=edit_product_description_handler),
    SwitchTo(
        Const(strings.buttons.back), state=states.Marketplace.VIEW_PRODUCT, id="back"
    ),
    state=states.Marketplace.EDIT_PRODUCT_DESCRIPTION,
    getter=product_getter,
)
