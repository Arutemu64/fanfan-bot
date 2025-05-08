from sqlalchemy import Select, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from fanfan.adapters.db.models import MarketORM, UserORM
from fanfan.core.dto.market import MarketDTO, MarketManagerDTO
from fanfan.core.dto.page import Pagination
from fanfan.core.models.market import Market, MarketId
from fanfan.core.models.user import UserId


def _select_market_dto() -> Select:
    return select(MarketORM).options(joinedload(MarketORM.managers))


def _parse_market_dto(market_orm: MarketORM) -> MarketDTO:
    return MarketDTO(
        id=market_orm.id,
        name=market_orm.name,
        description=market_orm.description,
        image_id=market_orm.image_id,
        is_visible=market_orm.is_visible,
        managers=[
            MarketManagerDTO(id=u.id, username=u.username) for u in market_orm.managers
        ],
    )


class MarketsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_market(self, market: Market) -> Market:
        market_orm = MarketORM.from_model(market)
        market_orm.managers = [await self.session.merge(u) for u in market_orm.managers]
        self.session.add(market_orm)
        await self.session.flush([market_orm])
        return market_orm.to_model()

    async def get_market_by_id(self, market_id: MarketId) -> Market | None:
        stmt = (
            select(MarketORM)
            .where(MarketORM.id == market_id)
            .with_for_update(of=MarketORM)
            .options(joinedload(MarketORM.managers))
        )
        market_orm = await self.session.scalar(stmt)
        return market_orm.to_model() if market_orm else None

    async def save_market(self, market: Market) -> Market:
        market_orm = await self.session.merge(MarketORM.from_model(market))
        return market_orm.to_model()

    async def read_market_by_id(self, market_id: MarketId) -> MarketDTO | None:
        stmt = _select_market_dto().where(MarketORM.id == market_id)
        market_orm = await self.session.scalar(stmt)
        return _parse_market_dto(market_orm) if market_orm else None

    async def read_markets(
        self,
        is_visible: bool,
        pagination: Pagination | None,
        user_id: UserId | None = None,
    ) -> list[MarketDTO]:
        stmt = (
            _select_market_dto()
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

        markets_orm = (await self.session.scalars(stmt)).unique()

        return [_parse_market_dto(m) for m in markets_orm]

    async def count_markets(self, is_visible: bool, user_id: UserId | None) -> int:
        stmt = select(func.count(MarketORM.id)).where(
            or_(
                MarketORM.is_visible == is_visible,
                MarketORM.managers.any(UserORM.id == user_id),
            )
        )
        return await self.session.scalar(stmt)
