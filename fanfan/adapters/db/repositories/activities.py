from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.adapters.db.models import ActivityORM
from fanfan.core.dto.page import Pagination
from fanfan.core.models.activity import Activity, ActivityId


class ActivitiesRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_activity_by_id(self, activity_id: ActivityId) -> Activity | None:
        stmt = select(ActivityORM).where(ActivityORM.id == activity_id)
        activity_orm = await self.session.scalar(stmt)
        return activity_orm.to_model() if activity_orm else None

    async def list_activities(
        self, pagination: Pagination | None = None
    ) -> list[Activity]:
        stmt = select(ActivityORM).order_by(ActivityORM.order)

        if pagination:
            stmt = stmt.limit(pagination.limit).offset(pagination.offset)

        activities_orm = await self.session.scalars(stmt)
        return [a.to_model() for a in activities_orm]

    async def count_activities(self) -> int:
        return await self.session.scalar(select(func.count(ActivityORM.id)))
