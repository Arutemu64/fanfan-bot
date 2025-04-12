from __future__ import annotations

from dataclasses import dataclass

from fanfan.adapters.db.repositories.achievements import AchievementsRepository
from fanfan.adapters.db.repositories.quest import QuestRepository
from fanfan.adapters.db.repositories.users import UsersRepository
from fanfan.core.exceptions.base import AppException
from fanfan.core.exceptions.users import UserNotFound
from fanfan.core.models.user import UserId
from fanfan.core.services.access import AccessService


@dataclass(frozen=True, slots=True)
class QuestStatsDTO:
    user_id: UserId
    can_participate_in_quest: bool
    points: int
    achievements_count: int
    total_achievements: int


class GetUserQuestStats:
    def __init__(
        self,
        users_repo: UsersRepository,
        quest_repo: QuestRepository,
        achievements: AchievementsRepository,
        access: AccessService,
    ) -> None:
        self.users_repo = users_repo
        self.quest_repo = quest_repo
        self.achievements = achievements
        self.access = access

    async def __call__(self, user_id: UserId) -> QuestStatsDTO:
        participant = await self.quest_repo.get_quest_participant(user_id=user_id)
        if participant is None:
            raise UserNotFound

        total = await self.achievements.count_achievements()

        try:
            user = await self.users_repo.get_user_by_id(user_id)
            self.access.ensure_can_participate_in_quest(user)
            can_participate_in_quest = True
        except AppException:
            can_participate_in_quest = False

        return QuestStatsDTO(
            user_id=participant.id,
            can_participate_in_quest=can_participate_in_quest,
            points=participant.points,
            achievements_count=participant.achievements_count,
            total_achievements=total,
        )
