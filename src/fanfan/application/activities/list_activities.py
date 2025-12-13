from dataclasses import dataclass

from fanfan.adapters.db.repositories.activities import ActivitiesRepository
from fanfan.core.dto.activity import ActivityDTO
from fanfan.core.dto.page import Page, Pagination


@dataclass(frozen=True, slots=True)
class ListActivitiesDTO:
    pagination: Pagination | None = None


class ListActivities:
    def __init__(self, activities_repo: ActivitiesRepository) -> None:
        self.activities_repo = activities_repo

    async def __call__(
        self,
        data: ListActivitiesDTO,
    ) -> Page[ActivityDTO]:
        return Page(
            items=await self.activities_repo.list_activities(data.pagination),
            total=await self.activities_repo.count_activities(),
        )
