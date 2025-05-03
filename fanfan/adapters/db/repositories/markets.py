from sqlalchemy import Select, delete, func, or_, select
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

    @staticmethod
    def _load_full(stmt: Select) -> Select:
        return stmt.options(joinedload(MarketORM.managers))

    async def add_market(self, market: Market) -> Market:
        market_orm = MarketORM.from_model(market)
        self.session.add(market_orm)
        await self.session.flush([market_orm])
        return market_orm.to_model()

    async def add_product(self, product: Product) -> Product:
        product_orm = ProductORM.from_model(product)
        self.session.add(product_orm)
        await self.session.flush([product_orm])
        return product_orm.to_model()

    async def get_market_by_id(self, market_id: MarketId) -> MarketFull | None:
        stmt = select(MarketORM).where(MarketORM.id == market_id)
        stmt = self._load_full(stmt)
        market_orm = await self.session.scalar(stmt)
        return market_orm.to_full_model() if market_orm else None

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

        markets_orm = await self.session.scalars(stmt)

        return [m.to_model() for m in markets_orm]

    async def count_markets(self, is_visible: bool, user_id: UserId | None) -> int:
        stmt = select(func.count(MarketORM.id)).where(
            or_(
                MarketORM.is_visible == is_visible,
                MarketORM.managers.any(UserORM.id == user_id),
            )
        )
        return await self.session.scalar(stmt)

    async def get_product_by_id(self, product_id: ProductId) -> Product | None:
        stmt = select(ProductORM).where(ProductORM.id == product_id)
        product_orm = await self.session.scalar(stmt)
        return product_orm.to_model() if product_orm else None

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

        products_orm = await self.session.scalars(stmt)

        return [p.to_model() for p in products_orm]

    async def count_products(self, market_id: MarketId) -> int:
        return await self.session.scalar(
            select(func.count(ProductORM.id)).where(ProductORM.market_id == market_id)
        )

    async def add_user_to_market_managers(self, user: User, market: Market) -> None:
        manager_orm = MarketManagerORM(
            market_id=market.id,
            user_id=user.id,
        )
        self.session.add(manager_orm)
        await self.session.flush([manager_orm])

    async def save_market(self, market: Market) -> Market:
        market_orm = await self.session.merge(MarketORM.from_model(market))
        return market_orm.to_model()

    async def save_product(self, product: Product) -> Product:
        product_orm = await self.session.merge(ProductORM.from_model(product))
        return product_orm.to_model()

    async def delete_product(self, product: Product) -> None:
        await self.session.execute(
            delete(ProductORM).where(ProductORM.id == product.id)
        )
