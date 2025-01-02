from __future__ import annotations

from dataclasses import dataclass

from fanfan.adapters.db.repositories.achievements import AchievementsRepository
from fanfan.adapters.db.repositories.quest import QuestRepository
from fanfan.adapters.db.repositories.users import UsersRepository
from fanfan.core.exceptions.users import UserNotFound
from fanfan.core.models.user import UserId


@dataclass(frozen=True, slots=True)
class QuestStatsDTO:
    user_id: UserId
    points: int
    achievements_count: int
    total_achievements: int


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

    async def __call__(self, user_id: UserId) -> QuestStatsDTO:
        participant = await self.quest_repo.get_quest_participant(user_id=user_id)
        if participant is None:
            raise UserNotFound

        total = await self.achievements.count_achievements()

        return QuestStatsDTO(
            user_id=participant.id,
            points=participant.points,
            achievements_count=participant.achievements_count,
            total_achievements=total,
        )
