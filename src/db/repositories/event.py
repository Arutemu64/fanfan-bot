from typing import Optional

from sqlalchemy import select
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
        statement = select(self.type_model).where(Event.current == True)  # noqa
        return (await self.session.execute(statement)).scalar_one_or_none()
