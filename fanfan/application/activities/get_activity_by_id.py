from fanfan.adapters.db.repositories.activities import ActivitiesRepository
from fanfan.core.exceptions.activities import ActivityNotFound
from fanfan.core.models.activity import Activity, ActivityId


class GetActivityById:
    def __init__(self, activities_repo: ActivitiesRepository) -> None:
        self.activities_repo = activities_repo

    async def __call__(self, activity_id: ActivityId) -> Activity:
        activity = await self.activities_repo.get_activity_by_id(activity_id)
        if activity:
            return activity
        raise ActivityNotFound
