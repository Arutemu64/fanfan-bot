from fanfan.adapters.db.repositories.achievements import (
    AchievementsRepository,
)
from fanfan.application.common.id_provider import IdProvider
from fanfan.core.dto.page import Page, Pagination
from fanfan.core.models.achievement import AchievementFull
from fanfan.core.models.user import UserId


class GetAchievementsPage:
    def __init__(
        self, achievements_repo: AchievementsRepository, id_provider: IdProvider
    ) -> None:
        self.achievements_repo = achievements_repo
        self.id_provider = id_provider

    async def __call__(
        self,
        pagination: Pagination | None = None,
        for_user_id: UserId | None = None,
    ) -> Page[AchievementFull]:
        achievements = await self.achievements_repo.list_achievements(
            user_id=for_user_id or self.id_provider.get_current_user_id(),
            pagination=pagination,
        )
        return Page(
            items=achievements,
            total=await self.achievements_repo.count_achievements(),
        )
