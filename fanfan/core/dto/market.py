from dataclasses import dataclass

from fanfan.core.models.market import MarketId
from fanfan.core.models.user import UserId
from fanfan.core.value_objects import TelegramFileId


@dataclass(kw_only=True, slots=True, frozen=True)
class MarketManagerDTO:
    id: UserId
    username: str


@dataclass(kw_only=True, slots=True, frozen=True)
class MarketDTO:
    id: MarketId
    name: str
    description: str | None
    image_id: TelegramFileId | None
    is_visible: bool

    managers: list[MarketManagerDTO]
