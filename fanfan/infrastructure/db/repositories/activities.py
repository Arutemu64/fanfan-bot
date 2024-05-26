from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.application.dto.activity import ActivityDTO
from fanfan.application.dto.common import Page
from fanfan.infrastructure.db.models import Activity
from fanfan.infrastructure.db.repositories.repo import Repository


class ActivitiesRepository(Repository[Activity]):
    def __init__(self, session: AsyncSession):
        self.session = session
        super().__init__(type_model=Activity, session=session)

    async def get_activity(self, activity_id: int) -> Optional[ActivityDTO]:
        activity = await self.session.get(Activity, activity_id)
        return activity.to_dto() if activity else None

    async def get_activities_page(
        self, page_number: int, activities_per_page: int
    ) -> Page[ActivityDTO]:
        query = select(Activity).order_by(Activity.order)
        page = await super()._paginate(
            query=query, page_number=page_number, items_per_page=activities_per_page
        )
        return Page(
            items=[a.to_dto() for a in page.items],
            number=page.number,
            total_pages=page.total_pages,
        )
