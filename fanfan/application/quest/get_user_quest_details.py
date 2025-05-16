from __future__ import annotations

from dataclasses import dataclass

from fanfan.adapters.db.repositories.achievements import AchievementsRepository
from fanfan.adapters.db.repositories.quest import QuestRepository
from fanfan.adapters.db.repositories.users import UsersRepository
from fanfan.core.exceptions.base import AppException
from fanfan.core.exceptions.users import UserNotFound
from fanfan.core.models.user import UserId
from fanfan.core.services.access import UserAccessValidator


@dataclass(frozen=True, slots=True)
class UserQuestStatsDTO:
    user_id: UserId
    can_participate_in_quest: bool
    points: int
    achievements_count: int
    rank: int | None
    total_achievements: int


class GetUserQuestStats:
    def __init__(
        self,
        users_repo: UsersRepository,
        quest_repo: QuestRepository,
        achievements_repo: AchievementsRepository,
        access: UserAccessValidator,
    ) -> None:
        self.users_repo = users_repo
        self.quest_repo = quest_repo
        self.achievements_repo = achievements_repo
        self.access = access

    async def __call__(self, user_id: UserId) -> UserQuestStatsDTO:
        player = await self.quest_repo.read_quest_player(user_id=user_id)
        if player is None:
            raise UserNotFound

        total = await self.achievements_repo.count_achievements()

        try:
            user = await self.users_repo.get_user_data(user_id)
            self.access.ensure_can_participate_in_quest(user)
            can_participate_in_quest = True
        except AppException:
            can_participate_in_quest = False

        return UserQuestStatsDTO(
            user_id=player.user_id,
            can_participate_in_quest=can_participate_in_quest,
            points=player.points,
            achievements_count=player.achievements_count,
            total_achievements=total,
            rank=player.rank,
        )
