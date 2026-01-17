from aiogram_dialog import Dialog

from fanfan.presentation.tgbot.dialogs.common.utils import merge_start_data

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

marketplace_dialog = Dialog(
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
    on_start=merge_start_data,
)
