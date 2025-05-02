from aiogram_dialog import Dialog, DialogManager

from fanfan.core.models.market import MarketId
from fanfan.presentation.tgbot import states

from .common import DATA_SELECTED_MARKET_ID
from .market.add_manager import (
    add_manager_window,
)
from .market.edit_market_description import (
    edit_market_description_window,
)
from .market.edit_market_image import (
    edit_market_image_window,
)
from .market.edit_market_name import (
    edit_market_name_window,
)
from .market.list_markets import (
    list_markets_window,
)
from .market.view_market import (
    view_market_window,
)
from .product.edit_product_description import (
    edit_product_description_window,
)
from .product.edit_product_image import (
    edit_product_image_window,
)
from .product.edit_product_name import (
    edit_product_name_window,
)
from .product.edit_product_price import (
    edit_product_price_window,
)
from .product.list_products import (
    view_products_window,
)
from .product.view_product import (
    delete_product_window,
    view_product_window,
)


async def open_market(manager: DialogManager, market_id: MarketId):
    await manager.start(
        state=states.Marketplace.VIEW_MARKET, data={DATA_SELECTED_MARKET_ID: market_id}
    )


async def on_start(start_data: dict | None, manager: DialogManager):
    if isinstance(start_data, dict):
        manager.dialog_data[DATA_SELECTED_MARKET_ID] = start_data.get(
            DATA_SELECTED_MARKET_ID
        )


dialog = Dialog(
    # Market
    list_markets_window,
    view_market_window,
    edit_market_name_window,
    edit_market_description_window,
    edit_market_image_window,
    add_manager_window,
    # Product
    view_products_window,
    view_product_window,
    edit_product_name_window,
    edit_product_description_window,
    edit_product_price_window,
    edit_product_image_window,
    delete_product_window,
    on_start=on_start,
)
