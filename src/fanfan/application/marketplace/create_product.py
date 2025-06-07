from dataclasses import dataclass

from fanfan.adapters.db.repositories.markets import MarketsRepository
from fanfan.adapters.db.repositories.products import ProductsRepository
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.application.common.id_provider import IdProvider
from fanfan.core.exceptions.market import MarketNotFound
from fanfan.core.models.market import Market
from fanfan.core.models.product import Product
from fanfan.core.services.market import MarketService
from fanfan.core.vo.market import MarketId
from fanfan.core.vo.telegram import TelegramFileId


@dataclass(kw_only=True, slots=True)
class CreateProductDTO:
    market_id: MarketId
    name: str
    description: str | None = None
    price: float = 0.0
    image_id: TelegramFileId | None = None


class CreateProduct:
    def __init__(
        self,
        markets_repo: MarketsRepository,
        products_repo: ProductsRepository,
        id_provider: IdProvider,
        uow: UnitOfWork,
        service: MarketService,
    ):
        self.markets_repo = markets_repo
        self.products_repo = products_repo
        self.id_provider = id_provider
        self.uow = uow
        self.service = service

    async def _get_market(self, market_id: MarketId) -> Market:
        market = await self.markets_repo.get_market_by_id(market_id)
        if market is None:
            raise MarketNotFound
        user = await self.id_provider.get_user_data()
        self.service.ensure_user_can_manage_market(market=market, manager=user)
        return market

    async def __call__(self, data: CreateProductDTO):
        async with self.uow:
            market = await self._get_market(data.market_id)
            product = Product(
                name=data.name,
                description=data.description,
                price=data.price,
                image_id=data.image_id,
                market_id=market.id,
            )
            await self.products_repo.add_product(product)
            await self.uow.commit()
