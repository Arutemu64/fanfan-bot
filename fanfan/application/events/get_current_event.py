from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from fanfan.core.exceptions.events import NoCurrentEvent
from fanfan.core.models.event import FullEventDTO
from fanfan.infrastructure.db.models import Event


class GetCurrentEvent:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def __call__(self) -> FullEventDTO:
        event = await self.session.scalar(
            select(Event)
            .where(Event.current.is_(True))
            .options(joinedload(Event.nomination), joinedload(Event.block))
        )
        if event:
            return event.to_full_dto()
        raise NoCurrentEvent
