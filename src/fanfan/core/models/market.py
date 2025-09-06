from dataclasses import dataclass

from fanfan.core.exceptions.market import (
    MarketDescTooLong,
    MarketNameTooLong,
)
from fanfan.core.vo.market import MarketId
from fanfan.core.vo.telegram import TelegramFileId

MAX_MARKET_NAME_LENGTH = 30
MAX_MARKET_DESCRIPTION_LENGTH = 300


@dataclass(kw_only=True, slots=True)
class Market:
    id: MarketId | None = None
    name: str
    description: str | None
    image_id: TelegramFileId | None
    is_visible: bool

    def set_name(self, new_name: str) -> None:
        if len(new_name) > MAX_MARKET_NAME_LENGTH:
            raise MarketNameTooLong
        self.name = new_name

    def set_description(self, new_description: str) -> None:
        if len(new_description) > MAX_MARKET_DESCRIPTION_LENGTH:
            raise MarketDescTooLong
        self.description = new_description
