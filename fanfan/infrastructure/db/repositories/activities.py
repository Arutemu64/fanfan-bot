from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.application.dto.common import Page
from fanfan.infrastructure.db.models import Activity
from fanfan.infrastructure.db.repositories.repo import Repository


class ActivitiesRepository(Repository[Activity]):
    def __init__(self, session: AsyncSession):
        self.session = session
        super().__init__(type_model=Activity, session=session)

    async def get_activity_page(self, page_number: int) -> Page[Activity]:
        query = select(Activity).order_by(Activity.id)
        return await super()._paginate(query, page_number, 1)
