from dataclasses import dataclass

from fanfan.adapters.db.repositories.activities import ActivitiesRepository
from fanfan.core.dto.activity import ActivityDTO
from fanfan.core.dto.page import Page, Pagination


@dataclass(frozen=True, slots=True)
class GetActivitiesPageDTO:
    pagination: Pagination | None = None


class GetActivitiesPage:
    def __init__(self, activities_repo: ActivitiesRepository) -> None:
        self.activities_repo = activities_repo

    async def __call__(
        self,
        data: GetActivitiesPageDTO,
    ) -> Page[ActivityDTO]:
        return Page(
            items=await self.activities_repo.list_activities(data.pagination),
            total=await self.activities_repo.count_activities(),
        )
