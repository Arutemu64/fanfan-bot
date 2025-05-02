from fanfan.adapters.db.repositories.markets import MarketsRepository
from fanfan.core.exceptions.market import MarketNotFound
from fanfan.core.models.market import MarketFull, MarketId


class GetMarket:
    def __init__(self, markets_repo: MarketsRepository):
        self.markets_repo = markets_repo

    async def __call__(self, market_id: MarketId) -> MarketFull:
        if market := await self.markets_repo.get_market_by_id(market_id):
            return market
        raise MarketNotFound
