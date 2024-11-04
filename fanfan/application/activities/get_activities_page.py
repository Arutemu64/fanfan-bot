from fanfan.adapters.db.repositories.activities import ActivitiesRepository
from fanfan.application.common.interactor import Interactor
from fanfan.core.dto.page import Page, Pagination
from fanfan.core.models.activity import ActivityModel


class GetActivitiesPage(Interactor[Pagination, Page[ActivityModel]]):
    def __init__(self, activities_repo: ActivitiesRepository) -> None:
        self.activities_repo = activities_repo

    async def __call__(
        self,
        pagination: Pagination | None = None,
    ) -> Page[ActivityModel]:
        return Page(
            items=await self.activities_repo.list_activities(pagination),
            total=await self.activities_repo.count_activities(),
        )
