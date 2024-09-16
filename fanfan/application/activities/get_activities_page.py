from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.core.models.activity import ActivityDTO
from fanfan.core.models.page import Page, Pagination
from fanfan.infrastructure.db.models import Activity


class GetActivitiesPage:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def __call__(
        self,
        pagination: Pagination | None = None,
    ) -> Page[ActivityDTO]:
        query = select(Activity).order_by(Activity.order)
        if pagination:
            query = query.limit(pagination.limit).offset(pagination.offset)

        activities = await self.session.scalars(query)
        total = await self.session.scalar(select(func.count(Activity.id)))

        return Page(
            items=[a.to_dto() for a in activities],
            total=total,
        )
