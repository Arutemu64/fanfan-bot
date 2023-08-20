from typing import Optional

from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Event
from .base import Repository


class EventRepo(Repository[Event]):
    """
    User repository for CRUD and other SQL queries
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize user repository as for all users or only for one user
        """
        super().__init__(type_model=Event, session=session)

    async def new(self, participant_id: int = None, title: str = None) -> Event:
        new_event = await self.session.merge(
            Event(participant_id=participant_id, title=title)
        )
        return new_event

    async def get_current(self) -> Optional[Event]:
        return await self.get_by_where(Event.current == True)  # noqa

    async def get_next(self, current_event: Event = None) -> Optional[Event]:
        if not current_event:
            current_event = await self.get_current()
        return await self.get_one(
            and_(Event.position > current_event.position, Event.hidden != True),  # noqa
            order_by=Event.position,
        )

    async def get_by_position(self, position: int) -> Optional[Event]:
        return await self.get_by_where(Event.position == position)
