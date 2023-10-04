from typing import Optional

from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import undefer

from ...bot.structures import Page
from ..models import Event, Participant
from .abstract import Repository


class ParticipantRepo(Repository[Participant]):
    def __init__(self, session: AsyncSession):
        super().__init__(type_model=Participant, session=session)

    async def new(self, title: str, nomination_id: str) -> Participant:
        new_participant = await self.session.merge(
            Participant(title=title, nomination_id=nomination_id)
        )
        return new_participant

    async def exists(self, participant_id: int) -> Optional[int]:
        return await super()._exists(Participant.id == participant_id)

    async def get(
        self,
        participant_id: int,
        nomination_id: Optional[str] = None,
        event_skip: Optional[bool] = None,
    ) -> Optional[Participant]:
        terms = [(Participant.id == participant_id)]
        if nomination_id:
            terms.append(Participant.nomination_id == nomination_id)
        if event_skip is not None:
            terms.append(Participant.event.has(Event.skip.is_(event_skip)))
        return await super()._get_by_where(query=and_(*terms))

    async def get_count(self) -> int:
        return await super()._get_count()

    async def paginate(
        self,
        page: int,
        participants_per_page: int,
        nomination_id: Optional[str] = None,
        event_skip: Optional[bool] = None,
        load_votes_count: bool = False,
    ) -> Page[Participant]:
        terms = []
        if nomination_id:
            terms.append(Participant.nomination_id == nomination_id)
        if event_skip is not None:
            terms.append(Participant.event.has(Event.skip.is_(event_skip)))
        return await super()._paginate(
            page=page,
            items_per_page=participants_per_page,
            query=and_(*terms),
            order_by=Participant.id,
            options=[undefer(Participant.votes_count)] if load_votes_count else None,
        )
