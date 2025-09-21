from fanfan.adapters.db.repositories.markets import MarketsRepository
from fanfan.application.common.id_provider import IdProvider
from fanfan.core.dto.market import MarketDTO
from fanfan.core.exceptions.market import MarketNotFound
from fanfan.core.vo.market import MarketId


class GetMarketById:
    def __init__(self, markets_repo: MarketsRepository, id_provider: IdProvider):
        self.markets_repo = markets_repo
        self.id_provider = id_provider

    async def __call__(self, market_id: MarketId) -> MarketDTO:
        user = await self.id_provider.get_current_user()
        if market := await self.markets_repo.read_market_by_id(market_id, user.id):
            return market
        raise MarketNotFound
