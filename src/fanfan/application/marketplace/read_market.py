from fanfan.adapters.db.repositories.markets import MarketsRepository
from fanfan.core.dto.market import MarketDTO
from fanfan.core.exceptions.market import MarketNotFound
from fanfan.core.vo.market import MarketId


class ReadMarket:
    def __init__(self, markets_repo: MarketsRepository):
        self.markets_repo = markets_repo

    async def __call__(self, market_id: MarketId) -> MarketDTO:
        if market := await self.markets_repo.read_market_by_id(market_id):
            return market
        raise MarketNotFound
