from dataclasses import dataclass, field
from typing import NewType

from fanfan.core.exceptions.market import (
    MarketDescTooLong,
    MarketNameTooLong,
    UserIsAlreadyMarketManager,
)
from fanfan.core.models.user import UserId
from fanfan.core.value_objects import TelegramFileId

MarketId = NewType("MarketId", int)

MAX_MARKET_NAME_LENGTH = 30
MAX_MARKET_DESCRIPTION_LENGTH = 300


@dataclass(kw_only=True, slots=True)
class Market:
    id: MarketId | None = None
    name: str
    description: str | None
    image_id: TelegramFileId | None
    is_visible: bool

    manager_ids: list[UserId] = field(default_factory=list)

    def set_name(self, new_name: str) -> None:
        if len(new_name) > MAX_MARKET_NAME_LENGTH:
            raise MarketNameTooLong
        self.name = new_name

    def set_description(self, new_description: str) -> None:
        if len(new_description) > MAX_MARKET_DESCRIPTION_LENGTH:
            raise MarketDescTooLong
        self.description = new_description

    def add_manager(self, user_id: UserId) -> None:
        if user_id in self.manager_ids:
            raise UserIsAlreadyMarketManager
        self.manager_ids.append(user_id)
