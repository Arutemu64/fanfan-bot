import typing

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.input import ManagedTextInput, TextInput
from aiogram_dialog.widgets.kbd import (
    Button,
    CurrentPage,
    FirstPage,
    LastPage,
    NextPage,
    PrevPage,
    Row,
    StubScroll,
    SwitchTo,
)
from aiogram_dialog.widgets.text import Const, Format, Jinja
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from fanfan.application.marketplace.create_product import (
    CreateProduct,
    CreateProductDTO,
)
from fanfan.application.marketplace.get_market_by_id import GetMarketById
from fanfan.application.marketplace.get_products_page import GetProductsPage
from fanfan.core.dto.page import Pagination
from fanfan.core.dto.user import FullUserDTO
from fanfan.core.vo.product import ProductId
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.utils import get_dialog_data_adapter
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.dialogs.marketplace.data import (
    MarketDialogData,
)
from fanfan.presentation.tgbot.middlewares.dialog_data_adapter import DialogDataAdapter
from fanfan.presentation.tgbot.static import strings
from fanfan.presentation.tgbot.templates import product_list

ID_PRODUCTS_SCROLL = "products_scroll"

if typing.TYPE_CHECKING:
    from aiogram_dialog.widgets.common import ManagedScroll


@inject
async def list_products_getter(
    dialog_manager: DialogManager,
    get_market: FromDishka[GetMarketById],
    get_products: FromDishka[GetProductsPage],
    dialog_data_adapter: DialogDataAdapter,
    current_user: FullUserDTO,
    **kwargs,
):
    dialog_data = dialog_data_adapter.load(MarketDialogData)
    scroll: ManagedScroll = dialog_manager.find(ID_PRODUCTS_SCROLL)
    market = await get_market(market_id=dialog_data.market_id)
    page = await get_products(
        market_id=market.id,
        pagination=Pagination(
            limit=current_user.settings.items_per_page,
            offset=await scroll.get_page() * current_user.settings.items_per_page,
        ),
    )
    pages = page.total // current_user.settings.items_per_page + bool(
        page.total % current_user.settings.items_per_page
    )
    return {
        "products": page.items,
        "pages": pages or 1,
        "market_name": market.name,
        "is_manager": current_user.id in (u.id for u in market.managers),
    }


async def product_id_input_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: str,
) -> None:
    dialog_data_adapter = get_dialog_data_adapter(dialog_manager)
    dialog_data = dialog_data_adapter.load(MarketDialogData)
    if "/" in data and data.replace("/", "").isnumeric():
        # User picked product
        dialog_data.product_id = ProductId(int(data.replace("/", "")))
        dialog_data_adapter.flush(dialog_data)
        await dialog_manager.switch_to(state=states.Marketplace.VIEW_PRODUCT)


@inject
async def add_product_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
    create_product: FromDishka[CreateProduct],
):
    dialog_data_adapter = get_dialog_data_adapter(manager)
    dialog_data = dialog_data_adapter.load(MarketDialogData)
    await create_product(
        CreateProductDTO(
            market_id=dialog_data.market_id,
            name="Новый товар",
        )
    )


view_products_window = Window(
    Title(Format("🛍️ {market_name}")),
    Jinja(product_list),
    Const("👆 Чтобы открыть карточку товара нажми на номер позиции"),
    Button(
        Const("➕ Создать товар"),
        when="is_manager",
        id="add_product",
        on_click=add_product_handler,
    ),
    StubScroll(ID_PRODUCTS_SCROLL, pages="pages"),
    Row(
        FirstPage(scroll=ID_PRODUCTS_SCROLL, text=Const("⏪")),
        PrevPage(scroll=ID_PRODUCTS_SCROLL, text=Const("◀️")),
        CurrentPage(
            scroll=ID_PRODUCTS_SCROLL,
            text=Format(text="{current_page1}/{pages}"),
        ),
        NextPage(scroll=ID_PRODUCTS_SCROLL, text=Const("▶️")),
        LastPage(scroll=ID_PRODUCTS_SCROLL, text=Const("⏭️")),
    ),
    SwitchTo(
        Const(strings.buttons.back), state=states.Marketplace.VIEW_MARKET, id="back"
    ),
    TextInput(id="product_id_input", on_success=product_id_input_handler),
    getter=list_products_getter,
    state=states.Marketplace.LIST_PRODUCTS,
)
