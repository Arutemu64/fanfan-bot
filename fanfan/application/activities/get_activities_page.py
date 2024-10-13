from fanfan.application.common.interactor import Interactor
from fanfan.core.models.activity import ActivityModel
from fanfan.core.models.page import Page, Pagination
from fanfan.infrastructure.db.repositories.activities import ActivitiesRepository


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
