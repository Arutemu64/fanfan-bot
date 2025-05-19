from dataclasses import dataclass

from fanfan.core.vo.market import MarketId
from fanfan.core.vo.product import ProductId
from fanfan.core.vo.telegram import TelegramFileId


@dataclass(frozen=True, slots=True, kw_only=True)
class ProductDTO:
    id: ProductId
    name: str
    description: str | None
    price: float
    image_id: TelegramFileId | None
    market_id: MarketId
