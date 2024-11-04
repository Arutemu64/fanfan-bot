from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.adapters.db.models import Activity
from fanfan.core.dto.page import Pagination
from fanfan.core.models.activity import ActivityId, ActivityModel


class ActivitiesRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_activity_by_id(self, activity_id: ActivityId) -> ActivityModel | None:
        activity = await self.session.get(Activity, activity_id)
        return activity.to_model() if activity else None

    async def list_activities(
        self, pagination: Pagination | None = None
    ) -> list[ActivityModel]:
        query = select(Activity).order_by(Activity.order)

        if pagination:
            query = query.limit(pagination.limit).offset(pagination.offset)

        activities = await self.session.scalars(query)
        return [a.to_model() for a in activities]

    async def count_activities(self) -> int:
        return await self.session.scalar(select(func.count(Activity.id)))
