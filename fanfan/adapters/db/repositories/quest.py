from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import undefer

from fanfan.adapters.db.models import UserORM
from fanfan.adapters.redis.dao.cache import CacheAdapter
from fanfan.core.dto.quest import QuestPlayerDTO, QuestRatingDTO
from fanfan.core.models.quest import QuestPlayer
from fanfan.core.models.user import UserId


def _user_orm_to_quest_player(user: UserORM) -> QuestPlayer:
    return QuestPlayer(id=UserId(user.id), points=user.points)


def _quest_player_to_user_orm(model: QuestPlayer) -> UserORM:
    return UserORM(id=model.id, points=model.points)


def _select_quest_player_dto() -> Select:
    return select(UserORM).options(
        undefer(UserORM.points),
        undefer(UserORM.achievements_count),
        undefer(UserORM.rank),
    )


def _parse_quest_player_dto(user_orm: UserORM) -> QuestPlayerDTO:
    return QuestPlayerDTO(
        user_id=user_orm.id,
        rank=user_orm.rank,
        username=user_orm.username,
        points=user_orm.points,
        achievements_count=user_orm.achievements_count,
    )


class QuestRepository:
    def __init__(self, session: AsyncSession, cache: CacheAdapter):
        self.session = session
        self.cache = cache

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
        user_orm = await self.session.scalar(stmt)
        return _parse_quest_player_dto(user_orm) if user_orm else None

    async def count_quest_players(self) -> int:
        return await self.session.scalar(
            select(func.count(UserORM.id)).where(UserORM.rank.isnot(None))
        )

    async def read_full_quest_rating(self) -> QuestRatingDTO:
        cache_key = "quest_rating"
        rating = await self.cache.get_cache(cache_key, QuestRatingDTO)
        if rating is None:
            stmt = (
                _select_quest_player_dto()
                .where(UserORM.rank.isnot(None))
                .order_by(UserORM.rank)
            )
            users = await self.session.scalars(stmt)
            players = [_parse_quest_player_dto(user_orm) for user_orm in users]
            total = await self.count_quest_players()
            rating = QuestRatingDTO(
                players=players,
                total=total,
            )
            await self.cache.set_cache(cache_key, rating, ttl=60)
        return rating
