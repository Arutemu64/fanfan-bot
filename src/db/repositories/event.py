from typing import Optional

from sqlalchemy import ColumnElement, and_, or_, true
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Event, Nomination, Participant
from .base import Repository


class EventRepo(Repository[Event]):
    """
    User repository for CRUD and other SQL queries
    """

    @staticmethod
    def get_events_query(
        include_hidden: bool, search_query: str = None
    ) -> ColumnElement:
        terms = [true()]
        if search_query:
            if search_query.isnumeric():
                terms.append(Event.id == int(search_query))
            else:
                terms.append(
                    or_(
                        Event.title.ilike(f"%{search_query}%"),
                        Event.participant.has(
                            Participant.title.ilike(f"%{search_query}%")
                        ),
                        Event.participant.has(
                            Participant.nomination.has(
                                Nomination.title.ilike(f"%{search_query}%")
                            )
                        ),
                    )
                )
        if not include_hidden:
            terms.append(Event.hidden.isnot(True))
        return and_(*terms)

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

    async def get_by_position(self, position: int) -> Optional[Event]:
        return await self.get_by_where(Event.real_position == position)

    async def get_current(self) -> Optional[Event]:
        return await self.get_by_where(Event.current.is_(True))

    async def get_next(self, current_event: Event) -> Optional[Event]:
        if current_event:
            return await self.get_by_where(
                Event.real_position == current_event.real_position + 1
            )
        else:
            return None
