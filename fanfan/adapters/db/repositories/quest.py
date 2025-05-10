from sqlalchemy import Row, Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import undefer

from fanfan.adapters.db.models import UserORM
from fanfan.core.dto.page import Pagination
from fanfan.core.dto.quest import QuestPlayerDTO
from fanfan.core.models.quest import QuestPlayer
from fanfan.core.models.user import UserId

ORDER_RULE = (UserORM.points + UserORM.achievements_count).desc()
WHERE_RULE = (UserORM.points + UserORM.achievements_count) > 0


def _user_orm_to_quest_player(user: UserORM) -> QuestPlayer:
    return QuestPlayer(id=UserId(user.id), points=user.points)


def _quest_player_to_user_orm(model: QuestPlayer) -> UserORM:
    return UserORM(id=model.id, points=model.points)


def _select_quest_player_dto() -> Select:
    return select(
        UserORM.id.label("user_id"),
        UserORM.username.label("username"),
        UserORM.points.label("points"),
        UserORM.achievements_count.label("achievements_count"),
        func.row_number().over(order_by=ORDER_RULE).label("rank"),
    )


def _parse_quest_player_dto(row: Row) -> QuestPlayerDTO:
    return QuestPlayerDTO(
        user_id=row.user_id,
        rank=row.rank,
        username=row.username,
        points=row.points,
        achievements_count=row.achievements_count,
    )


class QuestRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_player(self, user_id: UserId) -> QuestPlayer | None:
        stmt = (
            select(UserORM)
            .where(UserORM.id == user_id)
            .options(
                undefer(UserORM.points),
            )
            .with_for_update(of=[UserORM.points])
        )
        user_orm = await self.session.scalar(stmt)
        return _user_orm_to_quest_player(user_orm) if user_orm else None

    async def save_player(self, player: QuestPlayer) -> QuestPlayer:
        user_orm = await self.session.merge(_quest_player_to_user_orm(player))
        return _user_orm_to_quest_player(user_orm)

    async def read_quest_player(self, user_id: UserId) -> QuestPlayerDTO | None:
        stmt = _select_quest_player_dto().where(UserORM.id == user_id)
        result = (await self.session.execute(stmt)).first()
        return _parse_quest_player_dto(result) if result else None

    async def list_quest_players(
        self, pagination: Pagination | None = None
    ) -> list[QuestPlayerDTO]:
        stmt = _select_quest_player_dto().where(WHERE_RULE).order_by(ORDER_RULE)

        if pagination:
            stmt = stmt.limit(pagination.limit).offset(pagination.offset)

        results = (await self.session.execute(stmt)).all()

        return [_parse_quest_player_dto(row) for row in results]

    async def count_quest_players(self) -> int:
        return await self.session.scalar(
            select(func.count(UserORM.id)).where(WHERE_RULE)
        )
