from __future__ import annotations

from dataclasses import dataclass

from fanfan.core.exceptions.users import UserNotFound
from fanfan.core.models.user import UserId
from fanfan.infrastructure.db.repositories.achievements import AchievementsRepository
from fanfan.infrastructure.db.repositories.quest import QuestRepository
from fanfan.infrastructure.db.repositories.users import UsersRepository


@dataclass(frozen=True, slots=True)
class QuestStats:
    user_id: UserId
    points: int
    achievements_count: int
    total_achievements: int
    quest_registration: bool


class GetUserQuestStats:
    def __init__(
        self,
        users_repo: UsersRepository,
        quest_repo: QuestRepository,
        achievements: AchievementsRepository,
    ) -> None:
        self.users_repo = users_repo
        self.quest_repo = quest_repo
        self.achievements = achievements

    async def __call__(self, user_id: UserId) -> QuestStats:
        user = await self.users_repo.get_user_for_quest(user_id)
        if user is None:
            raise UserNotFound

        total = await self.achievements.count_achievements()

        return QuestStats(
            user_id=user.id,
            points=user.points,
            achievements_count=user.achievements_count,
            total_achievements=total,
            quest_registration=bool(user.quest_registration),
        )
