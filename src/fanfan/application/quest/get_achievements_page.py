from dataclasses import dataclass

from fanfan.adapters.db.repositories.achievements import AchievementsRepository
from fanfan.application.common.id_provider import IdProvider
from fanfan.core.dto.achievement import AchievementUserDTO
from fanfan.core.dto.page import Page, Pagination
from fanfan.core.vo.user import UserId


@dataclass(frozen=True, slots=True)
class GetAchievementsPageDTO:
    pagination: Pagination | None = None
    for_user_id: UserId | None = None


class GetAchievementsPage:
    def __init__(
        self, achievements_repo: AchievementsRepository, id_provider: IdProvider
    ) -> None:
        self.achievements_repo = achievements_repo
        self.id_provider = id_provider

    async def __call__(
        self,
        data: GetAchievementsPageDTO,
    ) -> Page[AchievementUserDTO]:
        current_user = await self.id_provider.get_current_user()
        achievements = await self.achievements_repo.list_achievements_for_user(
            user_id=data.for_user_id or current_user.id,
            pagination=data.pagination,
        )
        return Page(
            items=achievements,
            total=await self.achievements_repo.count_achievements(),
        )
