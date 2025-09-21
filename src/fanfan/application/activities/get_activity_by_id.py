from fanfan.adapters.db.repositories.activities import ActivitiesRepository
from fanfan.core.dto.activity import ActivityDTO
from fanfan.core.exceptions.activities import ActivityNotFound
from fanfan.core.vo.activity import ActivityId


class GetActivityById:
    def __init__(self, activities_repo: ActivitiesRepository) -> None:
        self.activities_repo = activities_repo

    async def __call__(self, activity_id: ActivityId) -> ActivityDTO:
        activity = await self.activities_repo.read_activity_by_id(activity_id)
        if activity:
            return activity
        raise ActivityNotFound
