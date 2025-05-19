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
from dishka import AsyncContainer

from fanfan.application.marketplace.create_product import (
    CreateProduct,
    CreateProductDTO,
)
from fanfan.application.marketplace.read_market import ReadMarket
from fanfan.application.marketplace.read_products_page import ReadProductsPage
from fanfan.core.dto.page import Pagination
from fanfan.core.models.user import UserData
from fanfan.core.vo.market import MarketId
from fanfan.core.vo.product import ProductId
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.dialogs.marketplace.common import (
    DATA_SELECTED_MARKET_ID,
    DATA_SELECTED_PRODUCT_ID,
)
from fanfan.presentation.tgbot.static import strings
from fanfan.presentation.tgbot.templates import product_list

ID_PRODUCTS_SCROLL = "products_scroll"

if typing.TYPE_CHECKING:
    from aiogram_dialog.widgets.common import ManagedScroll


async def list_products_getter(
    dialog_manager: DialogManager,
    container: AsyncContainer,
    user: UserData,
    **kwargs,
):
    market_id = MarketId(dialog_manager.dialog_data[DATA_SELECTED_MARKET_ID])
    scroll: ManagedScroll = dialog_manager.find(ID_PRODUCTS_SCROLL)

    get_market: ReadMarket = await container.get(ReadMarket)
    market = await get_market(market_id=market_id)
    get_products: ReadProductsPage = await container.get(ReadProductsPage)
    page = await get_products(
        market_id=market_id,
        pagination=Pagination(
            limit=user.settings.items_per_page,
            offset=await scroll.get_page() * user.settings.items_per_page,
        ),
    )
    return {
        "products": page.items,
        "pages": page.total // user.settings.items_per_page
        + bool(page.total % user.settings.items_per_page),
        "market_name": market.name,
        "is_manager": user.id in (u.id for u in market.managers),
    }


async def product_id_input_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: str,
) -> None:
    if "/" in data and data.replace("/", "").isnumeric():
        product_id = ProductId(int(data.replace("/", "")))
        dialog_manager.dialog_data[DATA_SELECTED_PRODUCT_ID] = product_id
        await dialog_manager.switch_to(state=states.Marketplace.VIEW_PRODUCT)


async def add_product_handler(
    callback: CallbackQuery, button: Button, manager: DialogManager
):
    container: AsyncContainer = manager.middleware_data["container"]
    create_product: CreateProduct = await container.get(CreateProduct)

    await create_product(
        CreateProductDTO(
            market_id=manager.dialog_data[DATA_SELECTED_MARKET_ID],
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
