from sqlalchemy import delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from fanfan.adapters.db.models import MarketManagerORM, MarketORM, ProductORM, UserORM
from fanfan.core.dto.page import Pagination
from fanfan.core.models.market import Market, MarketFull, MarketId
from fanfan.core.models.product import Product, ProductId
from fanfan.core.models.user import User, UserId


class MarketsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_market(self, model: Market) -> Market:
        market = MarketORM.from_model(model)
        self.session.add(market)
        await self.session.flush([market])
        return market.to_model()

    async def add_product(self, model: Product) -> Product:
        product = ProductORM.from_model(model)
        self.session.add(product)
        await self.session.flush([product])
        return product.to_model()

    async def get_market_by_id(self, market_id: MarketId) -> MarketFull | None:
        market = await self.session.get(
            MarketORM, market_id, options=[joinedload(MarketORM.managers)]
        )
        return market.to_full_model() if market else None

    async def list_markets(
        self,
        is_visible: bool,
        pagination: Pagination | None,
        user_id: UserId | None = None,
    ) -> list[Market]:
        stmt = (
            select(MarketORM)
            .where(
                or_(
                    MarketORM.is_visible == is_visible,
                    MarketORM.managers.any(UserORM.id == user_id),
                )
            )
            .order_by(MarketORM.order)
        )

        if pagination:
            stmt = stmt.limit(pagination.limit).offset(pagination.offset)

        markets = await self.session.scalars(stmt)

        return [m.to_model() for m in markets]

    async def count_markets(self, is_visible: bool, user_id: UserId | None) -> int:
        stmt = select(func.count(MarketORM.id)).where(
            or_(
                MarketORM.is_visible == is_visible,
                MarketORM.managers.any(UserORM.id == user_id),
            )
        )
        return await self.session.scalar(stmt)

    async def get_product_by_id(self, product_id: ProductId) -> Product | None:
        product = await self.session.get(ProductORM, product_id)
        return product.to_model() if product else None

    async def list_products(
        self, market_id: MarketId, pagination: Pagination
    ) -> list[Product]:
        stmt = (
            select(ProductORM)
            .where(ProductORM.market_id == market_id)
            .order_by(ProductORM.order)
        )

        if pagination:
            stmt = stmt.limit(pagination.limit).offset(pagination.offset)

        products = await self.session.scalars(stmt)

        return [p.to_model() for p in products]

    async def count_products(self, market_id: MarketId) -> int:
        return await self.session.scalar(
            select(func.count(ProductORM.id)).where(ProductORM.market_id == market_id)
        )

    async def add_user_to_market_managers(self, user: User, market: Market) -> None:
        manager = MarketManagerORM(
            market_id=market.id,
            user_id=user.id,
        )
        self.session.add(manager)
        await self.session.flush([manager])

    async def save_market(self, model: Market) -> Market:
        market = await self.session.merge(MarketORM.from_model(model))
        return market.to_model()

    async def save_product(self, model: Product) -> Product:
        product = await self.session.merge(ProductORM.from_model(model))
        return product.to_model()

    async def delete_product(self, model: Product) -> None:
        await self.session.execute(delete(ProductORM).where(ProductORM.id == model.id))
