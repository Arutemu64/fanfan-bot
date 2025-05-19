from fanfan.adapters.db.repositories.products import ProductsRepository
from fanfan.core.exceptions.market import ProductNotFound
from fanfan.core.vo.product import ProductId


class ReadProduct:
    def __init__(self, products_repo: ProductsRepository) -> None:
        self.products_repo = products_repo

    async def __call__(self, product_id: ProductId):
        if product := await self.products_repo.read_product(product_id):
            return product
        raise ProductNotFound
