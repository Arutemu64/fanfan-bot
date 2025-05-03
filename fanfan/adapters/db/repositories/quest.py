from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import undefer

from fanfan.adapters.db.models import UserORM
from fanfan.core.dto.page import Page, Pagination
from fanfan.core.dto.quest import PlayerRatingDTO
from fanfan.core.models.quest import Player, PlayerFull
from fanfan.core.models.user import UserId


class QuestRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _to_model(user: UserORM) -> Player:
        return Player(id=UserId(user.id), points=user.points)

    @staticmethod
    def _to_full_model(user: UserORM) -> PlayerFull:
        return PlayerFull(
            id=UserId(user.id),
            points=user.points,
            achievements_count=user.achievements_count,
        )

    @staticmethod
    def _from_model(model: Player) -> UserORM:
        return UserORM(id=model.id, points=model.points)

    async def get_player(self, user_id: UserId) -> PlayerFull | None:
        stmt = (
            select(UserORM)
            .where(UserORM.id == user_id)
            .options(
                undefer(UserORM.achievements_count),
                undefer(UserORM.points),
            )
            .execution_options(populate_existing=True)
            .with_for_update(of=[UserORM.points])
        )
        player = await self.session.scalar(stmt)
        return self._to_full_model(player) if player else None

    async def read_quest_rating_page(
        self, pagination: Pagination | None = None
    ) -> Page[PlayerRatingDTO]:
        order_rule = (UserORM.points + UserORM.achievements_count).desc()
        where_rule = (UserORM.points + UserORM.achievements_count) > 0
        stmt = (
            select(
                func.row_number().over(order_by=order_rule).label("position"),
                UserORM.username,
                UserORM.points,
                UserORM.achievements_count,
            )
            .where(where_rule)
            .order_by(order_rule)
        )
        total_stmt = select(func.count(UserORM.id)).where(where_rule)

        if pagination:
            stmt = stmt.limit(pagination.limit).offset(pagination.offset)

        results = (await self.session.execute(stmt)).all()
        total = await self.session.scalar(total_stmt)

        return Page(
            items=[
                PlayerRatingDTO(
                    position=row.position,
                    username=row.username,
                    points=row.points,
                    achievements_count=row.achievements_count,
                )
                for row in results
            ],
            total=total,
        )

    async def save_player(self, player: Player) -> Player:
        user_orm = await self.session.merge(self._from_model(player))
        return self._to_model(user_orm)
