from dataclasses import dataclass

from fanfan.core.exceptions.market import (
    NegativeProductPrice,
    ProductDescTooLong,
    ProductNameTooLong,
)
from fanfan.core.vo.market import MarketId
from fanfan.core.vo.product import ProductId
from fanfan.core.vo.telegram import TelegramFileId

MAX_PRODUCT_NAME_LENGTH = 30
MAX_PRODUCT_DESCRIPTION_LENGTH = 300


@dataclass(kw_only=True, slots=True)
class Product:
    id: ProductId | None = None
    name: str
    description: str | None
    price: float
    image_id: TelegramFileId | None
    market_id: MarketId

    def set_name(self, name: str) -> None:
        if len(name) > MAX_PRODUCT_NAME_LENGTH:
            raise ProductNameTooLong
        self.name = name

    def set_description(self, description: str) -> None:
        if len(description) > MAX_PRODUCT_DESCRIPTION_LENGTH:
            raise ProductDescTooLong
        self.description = description

    def set_price(self, price: float) -> None:
        if price < 0:
            raise NegativeProductPrice
        self.price = price
