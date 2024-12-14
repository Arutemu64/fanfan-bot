from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.adapters.db.models import DBActivity
from fanfan.core.dto.page import Pagination
from fanfan.core.models.activity import Activity, ActivityId


class ActivitiesRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_activity_by_id(self, activity_id: ActivityId) -> Activity | None:
        activity = await self.session.get(DBActivity, activity_id)
        return activity.to_model() if activity else None

    async def list_activities(
        self, pagination: Pagination | None = None
    ) -> list[Activity]:
        query = select(DBActivity).order_by(DBActivity.order)

        if pagination:
            query = query.limit(pagination.limit).offset(pagination.offset)

        activities = await self.session.scalars(query)
        return [a.to_model() for a in activities]

    async def count_activities(self) -> int:
        return await self.session.scalar(select(func.count(DBActivity.id)))
