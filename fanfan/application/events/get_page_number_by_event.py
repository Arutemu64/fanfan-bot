import math

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.infrastructure.db.models import Event


class GetPageNumberByEvent:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def __call__(
        self,
        event_id: int,
        events_per_page: int,
    ) -> int | None:
        order_query = select(Event.order).where(Event.id == event_id).scalar_subquery()
        position_query = select(func.count(Event.id)).where(Event.order <= order_query)
        event_position = await self.session.scalar(position_query)
        if event_position > 0:
            return math.floor((event_position - 1) / events_per_page)
        return None
