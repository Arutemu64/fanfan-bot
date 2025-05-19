from fanfan.adapters.db.repositories.products import ProductsRepository
from fanfan.core.dto.page import Page, Pagination
from fanfan.core.dto.product import ProductDTO
from fanfan.core.vo.market import MarketId


class ReadProductsPage:
    def __init__(self, products_repo: ProductsRepository):
        self.products_repo = products_repo

    async def __call__(
        self, market_id: MarketId, pagination: Pagination
    ) -> Page[ProductDTO]:
        products = await self.products_repo.read_products(market_id, pagination)
        total = await self.products_repo.count_products(market_id)
        return Page(
            items=products,
            total=total,
        )
