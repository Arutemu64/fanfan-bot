from fanfan.adapters.db.repositories.markets import MarketsRepository
from fanfan.adapters.db.repositories.products import ProductsRepository
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.application.common.id_provider import IdProvider
from fanfan.core.exceptions.market import (
    ProductNotFound,
)
from fanfan.core.models.product import Product
from fanfan.core.services.access import UserAccessValidator
from fanfan.core.vo.product import ProductId
from fanfan.core.vo.telegram import TelegramFileId


class UpdateProduct:
    def __init__(
        self,
        products_repo: ProductsRepository,
        markets_repo: MarketsRepository,
        id_provider: IdProvider,
        uow: UnitOfWork,
        access: UserAccessValidator,
    ):
        self.products_repo = products_repo
        self.markets_repo = markets_repo
        self.id_provider = id_provider
        self.uow = uow
        self.access = access

    async def _get_product(self, product_id: ProductId) -> Product:
        product = await self.products_repo.get_product_by_id(product_id)
        if product is None:
            raise ProductNotFound
        market = await self.markets_repo.get_market_by_id(product.market_id)
        user = await self.id_provider.get_user_data()
        self.access.ensure_can_edit_market(market=market, manager=user)
        return product

    async def update_product_name(self, product_id: ProductId, new_name: str) -> None:
        async with self.uow:
            product = await self._get_product(product_id)
            product.set_name(new_name)
            await self.products_repo.save_product(product)
            await self.uow.commit()

    async def update_product_description(
        self, product_id: ProductId, new_description: str
    ) -> None:
        async with self.uow:
            product = await self._get_product(product_id)
            product.set_description(new_description)
            await self.products_repo.save_product(product)
            await self.uow.commit()

    async def update_product_price(
        self, product_id: ProductId, new_price: float
    ) -> None:
        async with self.uow:
            product = await self._get_product(product_id)
            product.set_price(new_price)
            await self.products_repo.save_product(product)
            await self.uow.commit()

    async def update_product_image(
        self, product_id: ProductId, new_image_id: TelegramFileId | None
    ) -> None:
        async with self.uow:
            product = await self._get_product(product_id)
            product.image_id = new_image_id
            await self.products_repo.save_product(product)
            await self.uow.commit()

    async def delete_product(self, product_id: ProductId) -> None:
        async with self.uow:
            product = await self._get_product(product_id)
            await self.products_repo.delete_product(product)
            await self.uow.commit()
