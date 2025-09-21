from __future__ import annotations

from dataclasses import dataclass

from fanfan.adapters.db.repositories.achievements import AchievementsRepository
from fanfan.adapters.db.repositories.quest import QuestRepository
from fanfan.adapters.db.repositories.tickets import TicketsRepository
from fanfan.adapters.db.repositories.users import UsersRepository
from fanfan.core.exceptions.base import AccessDenied
from fanfan.core.exceptions.users import UserNotFound
from fanfan.core.services.quest import QuestService
from fanfan.core.vo.user import UserId


@dataclass(frozen=True, slots=True, kw_only=True)
class UserQuestStatusDTO:
    user_id: UserId

    can_participate_in_quest: bool
    reason: str | None

    points: int
    achievements_count: int
    rank: int | None
    total_achievements: int


class GetUserQuestStatus:
    def __init__(
        self,
        users_repo: UsersRepository,
        quest_repo: QuestRepository,
        tickets_repo: TicketsRepository,
        achievements_repo: AchievementsRepository,
        service: QuestService,
    ) -> None:
        self.users_repo = users_repo
        self.quest_repo = quest_repo
        self.tickets_repo = tickets_repo
        self.achievements_repo = achievements_repo
        self.service = service

    async def __call__(self, user_id: UserId) -> UserQuestStatusDTO:
        player = await self.quest_repo.read_quest_player(user_id=user_id)
        if player is None:
            raise UserNotFound

        reason = None
        try:
            user = await self.users_repo.get_user_by_id(user_id)
            if user is None:
                raise UserNotFound
            ticket = await self.tickets_repo.get_ticket_by_user_id(user.id)
            self.service.ensure_user_can_participate_in_quest(user=user, ticket=ticket)
            can_participate_in_quest = True
        except AccessDenied as e:
            can_participate_in_quest = False
            reason = e.message

        total = await self.achievements_repo.count_achievements()

        return UserQuestStatusDTO(
            user_id=player.user_id,
            can_participate_in_quest=can_participate_in_quest,
            reason=reason,
            points=player.points,
            achievements_count=player.achievements_count,
            total_achievements=total,
            rank=player.rank,
        )
