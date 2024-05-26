from fanfan.application.dto.activity import ActivityDTO
from fanfan.application.dto.common import Page
from fanfan.application.exceptions.activities import ActivityNotFound
from fanfan.application.services.base import BaseService


class ActivitiesService(BaseService):
    async def get_activity(self, activity_id: int) -> ActivityDTO:
        if activity := await self.uow.activities.get_activity(activity_id):
            return activity
        raise ActivityNotFound

    async def get_activities_page(
        self, page_number: int, activities_per_page: int
    ) -> Page[ActivityDTO]:
        return await self.uow.activities.get_activities_page(
            page_number=page_number,
            activities_per_page=activities_per_page,
        )
