from fanfan.adapters.db.repositories.markets import MarketsRepository
from fanfan.core.exceptions.market import ProductNotFound
from fanfan.core.models.product import ProductId


class GetProduct:
    def __init__(self, markets_repo: MarketsRepository):
        self.markets_repo = markets_repo

    async def __call__(self, product_id: ProductId):
        if product := await self.markets_repo.get_product_by_id(product_id):
            return product
        raise ProductNotFound
