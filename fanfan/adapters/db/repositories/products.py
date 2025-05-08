from sqlalchemy import Select, delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.adapters.db.models import ProductORM
from fanfan.core.dto.page import Pagination
from fanfan.core.dto.product import ProductDTO
from fanfan.core.models.market import MarketId
from fanfan.core.models.product import Product, ProductId


def _select_product_dto() -> Select:
    return select(ProductORM)


def _parse_product_dto(product_orm: ProductORM) -> ProductDTO:
    return ProductDTO(
        id=product_orm.id,
        name=product_orm.name,
        description=product_orm.description,
        price=product_orm.price,
        image_id=product_orm.image_id,
        market_id=product_orm.market_id,
    )


class ProductsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_product(self, product: Product) -> Product:
        product_orm = ProductORM.from_model(product)
        self.session.add(product_orm)
        await self.session.flush([product_orm])
        return product_orm.to_model()

    async def get_product_by_id(self, product_id: ProductId) -> Product | None:
        stmt = select(ProductORM).where(ProductORM.id == product_id)
        product_orm = await self.session.scalar(stmt)
        return product_orm.to_model() if product_orm else None

    async def save_product(self, product: Product) -> Product:
        product_orm = await self.session.merge(ProductORM.from_model(product))
        return product_orm.to_model()

    async def delete_product(self, product: Product) -> None:
        await self.session.execute(
            delete(ProductORM).where(ProductORM.id == product.id)
        )

    async def read_product(self, product_id: ProductId) -> ProductDTO | None:
        stmt = _select_product_dto().where(ProductORM.id == product_id)
        product_orm = await self.session.scalar(stmt)
        return _parse_product_dto(product_orm) if product_orm else None

    async def read_products(
        self, market_id: MarketId, pagination: Pagination
    ) -> list[ProductDTO]:
        stmt = (
            _select_product_dto()
            .where(ProductORM.market_id == market_id)
            .order_by(ProductORM.order)
        )

        if pagination:
            stmt = stmt.limit(pagination.limit).offset(pagination.offset)

        products_orm = await self.session.scalars(stmt)

        return [_parse_product_dto(p) for p in products_orm]

    async def count_products(self, market_id: MarketId) -> int:
        return await self.session.scalar(
            select(func.count(ProductORM.id)).where(ProductORM.market_id == market_id)
        )
