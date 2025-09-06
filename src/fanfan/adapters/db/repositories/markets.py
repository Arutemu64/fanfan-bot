from sqlalchemy import Select, and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from fanfan.adapters.db.models import (
    MarketORM,
    PermissionORM,
    UserPermissionORM,
)
from fanfan.core.constants.permissions import Permissions
from fanfan.core.dto.market import MarketDTO, MarketManagerDTO
from fanfan.core.dto.page import Pagination
from fanfan.core.models.market import Market
from fanfan.core.vo.market import MarketId
from fanfan.core.vo.user import UserId


def _parse_market_dto(market_orm: MarketORM) -> MarketDTO:
    return MarketDTO(
        id=market_orm.id,
        name=market_orm.name,
        description=market_orm.description,
        is_visible=market_orm.is_visible,
        image_id=market_orm.image_id,
        managers=[
            MarketManagerDTO(id=m.user.id, username=m.user.username)
            for m in market_orm.permissions
        ],
    )


def _filter_visible_markets(stmt: Select, user_id: UserId) -> Select:
    user_can_manage = MarketORM.permissions.any(
        and_(
            UserPermissionORM.user_id == user_id,
            UserPermissionORM.permission.has(
                PermissionORM.name == Permissions.CAN_MANAGE_MARKET
            ),
        )
    )
    return stmt.where(or_(MarketORM.is_visible.is_(True), user_can_manage))


class MarketsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_market(self, market: Market) -> Market:
        market_orm = MarketORM.from_model(market)
        self.session.add(market_orm)
        await self.session.flush([market_orm])
        return market_orm.to_model()

    async def get_market_by_id(self, market_id: MarketId) -> Market | None:
        stmt = (
            select(MarketORM)
            .where(MarketORM.id == market_id)
            .with_for_update(of=MarketORM)
        )
        market_orm = await self.session.scalar(stmt)
        return market_orm.to_model() if market_orm else None

    async def save_market(self, market: Market) -> Market:
        market_orm = await self.session.merge(MarketORM.from_model(market))
        return market_orm.to_model()

    async def read_market_by_id(
        self, market_id: MarketId, user_id: UserId
    ) -> MarketDTO | None:
        stmt = select(MarketORM).where(MarketORM.id == market_id)
        stmt = _filter_visible_markets(stmt, user_id)

        # Load managers
        stmt = stmt.options(
            joinedload(MarketORM.permissions).joinedload(UserPermissionORM.user)
        )

        market_orm = await self.session.scalar(stmt)

        return _parse_market_dto(market_orm) if market_orm else None

    async def read_markets(
        self,
        pagination: Pagination | None,
        user_id: UserId | None = None,
    ) -> list[MarketDTO]:
        stmt = select(MarketORM)
        stmt = _filter_visible_markets(stmt, user_id)
        if pagination:
            stmt = stmt.limit(pagination.limit).offset(pagination.offset)

        stmt = stmt.options(
            joinedload(MarketORM.permissions).joinedload(UserPermissionORM.user)
        )

        result = (await self.session.scalars(stmt)).unique()

        return [_parse_market_dto(market_orm) for market_orm in result]

    async def count_markets(self, user_id: UserId | None) -> int:
        stmt = _filter_visible_markets(select(func.count(MarketORM.id)), user_id)
        return await self.session.scalar(stmt)
