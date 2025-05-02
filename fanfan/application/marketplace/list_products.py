from fanfan.adapters.db.repositories.markets import MarketsRepository
from fanfan.core.dto.page import Page, Pagination
from fanfan.core.models.market import MarketId
from fanfan.core.models.product import Product


class GetProducts:
    def __init__(self, markets_repo: MarketsRepository):
        self.markets_repo = markets_repo

    async def __call__(
        self, market_id: MarketId, pagination: Pagination
    ) -> Page[Product]:
        products = await self.markets_repo.list_products(market_id, pagination)
        total = await self.markets_repo.count_products(market_id)
        return Page(
            items=products,
            total=total,
        )
