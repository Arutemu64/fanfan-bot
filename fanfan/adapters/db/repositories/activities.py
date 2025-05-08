from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.adapters.db.models import ActivityORM
from fanfan.core.dto.activity import ActivityDTO
from fanfan.core.dto.page import Pagination
from fanfan.core.models.activity import ActivityId


def _parse_activity_dto(activity_orm: ActivityORM) -> ActivityDTO:
    return ActivityDTO(
        id=activity_orm.id,
        title=activity_orm.title,
        description=activity_orm.description,
        image_path=Path(activity_orm.image.path) if activity_orm.image else None,
    )


class ActivitiesRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def read_activity_by_id(self, activity_id: ActivityId) -> ActivityDTO | None:
        stmt = select(ActivityORM).where(ActivityORM.id == activity_id)
        activity_orm = await self.session.scalar(stmt)
        return _parse_activity_dto(activity_orm) if activity_orm else None

    async def list_activities(
        self, pagination: Pagination | None = None
    ) -> list[ActivityDTO]:
        stmt = select(ActivityORM).order_by(ActivityORM.order)

        if pagination:
            stmt = stmt.limit(pagination.limit).offset(pagination.offset)

        activities_orm = await self.session.scalars(stmt)
        return [_parse_activity_dto(a) for a in activities_orm]

    async def count_activities(self) -> int:
        return await self.session.scalar(select(func.count(ActivityORM.id)))
