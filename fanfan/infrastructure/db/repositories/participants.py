from typing import Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager, joinedload, undefer

from fanfan.application.dto.common import Page
from fanfan.infrastructure.db.models import Event, Nomination, Participant, Vote
from fanfan.infrastructure.db.repositories.repo import Repository


class ParticipantsRepository(Repository[Participant]):
    def __init__(self, session: AsyncSession):
        self.session = session
        super().__init__(type_model=Participant, session=session)

    async def get_participant(self, participant_id: int) -> Optional[Participant]:
        return await self.session.get(
            Participant,
            participant_id,
            options=[joinedload(Participant.nomination), joinedload(Participant.event)],
        )

    async def get_participant_by_title(self, title: str) -> Optional[Participant]:
        query = select(Participant).where(Participant.title == title).limit(1)
        return await self.session.scalar(query)

    async def paginate_participants(
        self,
        page_number: int,
        participants_per_page: int,
        only_votable: Optional[bool] = None,
        nomination_id: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> Page[Participant]:
        query = (
            select(Participant)
            .order_by(Participant.id)
            .options(undefer(Participant.votes_count))
        )
        if only_votable:
            query = query.where(
                and_(
                    Participant.nomination.has(Nomination.votable.is_(True)),
                    Participant.event.has(Event.skip.isnot(True)),
                )
            )
        if nomination_id:
            query = query.where(
                Participant.nomination.has(Nomination.id == nomination_id)
            )
        if user_id:
            query = query.options(contains_eager(Participant.user_vote)).outerjoin(
                Vote,
                and_(
                    Vote.participant_id == Participant.id,
                    Vote.user_id == user_id,
                ),
            )
        return await super()._paginate(query, page_number, participants_per_page)
