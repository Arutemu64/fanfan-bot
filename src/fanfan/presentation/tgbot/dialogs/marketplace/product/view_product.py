from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Group, SwitchTo
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.text import Const, Jinja, Multi
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from fanfan.application.marketplace.update_product import UpdateProduct
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.utils import get_dialog_data_adapter
from fanfan.presentation.tgbot.dialogs.marketplace.data import (
    MarketDialogData,
)
from fanfan.presentation.tgbot.dialogs.marketplace.product.common import product_getter
from fanfan.presentation.tgbot.static import strings


@inject
async def delete_product_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
    update_product: FromDishka[UpdateProduct],
):
    dialog_data_adapter = get_dialog_data_adapter(manager)
    dialog_data = dialog_data_adapter.load(MarketDialogData)
    await update_product.delete_product(product_id=dialog_data.product_id)
    await callback.answer(strings.common.success)
    await manager.switch_to(state=states.Marketplace.LIST_PRODUCTS)


delete_product_window = Window(
    Jinja("⚠️ Вы уверены, что хотите удалить товар <b>{{ product_name }}</b>?"),
    Button(
        Const("♻️ Да, удалить"),
        id="delete_product",
        on_click=delete_product_handler,
    ),
    SwitchTo(
        Const(strings.buttons.back),
        state=states.Marketplace.VIEW_PRODUCT,
        id="back",
    ),
    getter=product_getter,
    state=states.Marketplace.CONFIRM_PRODUCT_DELETE,
)


view_product_window = Window(
    DynamicMedia(
        selector="product_image",
        when="product_image",
    ),
    Jinja("<b>📦 {{ product_name|upper }}</b>"),
    Jinja(" └ <i>(из магазина <b>{{ market_name }}</b>)</i>"),
    Const(" "),
    Multi(
        Jinja("{{ product_description }}"),
        Const(" "),
        when="product_description",
    ),
    Jinja(
        "💵 Стоимость: "
        "{{ '%.2f' % product_price if product_price % 1 != 0 else product_price|int }}₽"
    ),
    Group(
        SwitchTo(
            Const("✏️ Изменить название"),
            state=states.Marketplace.EDIT_PRODUCT_NAME,
            id="edit_product_name",
        ),
        SwitchTo(
            Const("💬 Изменить описание"),
            state=states.Marketplace.EDIT_PRODUCT_DESCRIPTION,
            id="edit_product_description",
        ),
        SwitchTo(
            Const("💸 Изменить цену"),
            state=states.Marketplace.EDIT_PRODUCT_PRICE,
            id="edit_product_price",
        ),
        SwitchTo(
            Const("🖼️ Изменить изображение"),
            state=states.Marketplace.EDIT_PRODUCT_IMAGE,
            id="edit_product_picture",
        ),
        SwitchTo(
            Const("🗑️ Удалить товар"),
            id="delete_product",
            state=states.Marketplace.CONFIRM_PRODUCT_DELETE,
        ),
        when="market_is_manager",
    ),
    SwitchTo(
        Const(strings.buttons.back), state=states.Marketplace.LIST_PRODUCTS, id="back"
    ),
    getter=product_getter,
    state=states.Marketplace.VIEW_PRODUCT,
)
