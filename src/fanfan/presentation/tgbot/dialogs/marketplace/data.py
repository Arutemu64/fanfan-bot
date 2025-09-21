from dataclasses import dataclass

from fanfan.core.vo.market import MarketId
from fanfan.core.vo.product import ProductId


@dataclass(slots=True)
class MarketDialogData:
    market_id: MarketId | None = None
    product_id: ProductId | None = None
