from typing import Optional

from fanfan.application.dto.activity import ActivityDTO
from fanfan.application.dto.common import Page
from fanfan.application.services.base import BaseService


class CommonService(BaseService):
    async def get_activity_page(self, page_number: int) -> Page[ActivityDTO]:
        page = await self.uow.activities.get_activity_page(page_number)
        return Page(
            items=[a.to_dto() for a in page.items],
            number=page.number,
            total_pages=page.total_pages,
        )

    async def get_random_quote(self) -> Optional[str]:
        return await self.uow.quotes.get_random_quote()
