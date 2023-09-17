from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Event
from .abstract import Repository


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

    async def get_count(self, query=None) -> int:
        if query is None:
            statement = select(func.max(Event.position))
        else:
            statement = select(func.count()).select_from(self.type_model).where(query)
        return (await self.session.execute(statement)).scalar()

    async def get_by_position(self, position: int) -> Optional[Event]:
        return await self.get_by_where(Event.real_position == position)

    async def get_current(self) -> Optional[Event]:
        return await self.get_by_where(Event.current.is_(True))

    async def get_next(self, current_event: Event) -> Optional[Event]:
        if current_event:
            return await self.get_by_where(
                Event.real_position == current_event.real_position + 1,
            )
        else:
            return None
