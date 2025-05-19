from dataclasses import dataclass

from fanfan.core.vo.market import MarketId
from fanfan.core.vo.telegram import TelegramFileId
from fanfan.core.vo.user import UserId


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
