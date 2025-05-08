from fanfan.adapters.db.repositories.activities import ActivitiesRepository
from fanfan.core.dto.activity import ActivityDTO
from fanfan.core.dto.page import Page, Pagination


class GetActivitiesPage:
    def __init__(self, activities_repo: ActivitiesRepository) -> None:
        self.activities_repo = activities_repo

    async def __call__(
        self,
        pagination: Pagination | None = None,
    ) -> Page[ActivityDTO]:
        return Page(
            items=await self.activities_repo.list_activities(pagination),
            total=await self.activities_repo.count_activities(),
        )
