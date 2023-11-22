from typing import Optional

from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession

from ...bot.structures import Page
from ..models import Event, Nomination, Participant
from .abstract import Repository


class ParticipantRepo(Repository[Participant]):
    def __init__(self, session: AsyncSession):
        super().__init__(type_model=Participant, session=session)

    async def new(self, title: str, nomination: Nomination) -> Participant:
        new_participant = await self.session.merge(
            Participant(title=title, nomination=nomination)
        )
        return new_participant

    async def get(self, participant_id: int) -> Optional[Participant]:
        return await super()._get(participant_id)

    async def get_by_title(self, title: str) -> Optional[Participant]:
        return await super()._get_by_where(Participant.title == title)

    async def paginate(
        self,
        page: int,
        participants_per_page: int,
        nomination: Nomination,
        hide_event_skip: bool = False,
    ) -> Page[Participant]:
        terms = [Participant.nomination == nomination]
        if hide_event_skip:
            terms.append(Participant.event.has(Event.skip.isnot(True)))
        return await super()._paginate(
            page=page,
            items_per_page=participants_per_page,
            query=and_(*terms),
            order_by=Participant.id,
        )
