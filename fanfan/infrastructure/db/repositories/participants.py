from typing import Optional

from sqlalchemy import and_, case, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager, joinedload, undefer

from fanfan.application.dto.common import Page
from fanfan.application.dto.participant import (
    CreateParticipantDTO,
    FullParticipantDTO,
    ParticipantDTO,
    VotingParticipantDTO,
)
from fanfan.infrastructure.db.models import Event, Nomination, Participant, Vote
from fanfan.infrastructure.db.repositories.repo import Repository


class ParticipantsRepository(Repository[Participant]):
    def __init__(self, session: AsyncSession):
        self.session = session
        super().__init__(type_model=Participant, session=session)

    async def add_participant(self, dto: CreateParticipantDTO) -> ParticipantDTO:
        participant = Participant(**dto.model_dump(exclude_unset=True))
        self.session.add(participant)
        await self.session.flush([participant])
        return participant.to_dto()

    async def get_participant(
        self, participant_id: int
    ) -> Optional[FullParticipantDTO]:
        participant = await self.session.get(
            Participant,
            participant_id,
            options=[joinedload(Participant.nomination), joinedload(Participant.event)],
        )
        return participant.to_full_dto() if participant else None

    async def get_participant_by_title(
        self, title: str
    ) -> Optional[FullParticipantDTO]:
        query = (
            select(Participant)
            .where(Participant.title == title)
            .options(joinedload(Participant.event), joinedload(Participant.nomination))
            .limit(1)
        )
        participant = await self.session.scalar(query)
        return participant.to_full_dto() if participant else None

    async def get_participant_by_scoped_id(
        self, nomination_id: str, scoped_id: int
    ) -> Optional[FullParticipantDTO]:
        query = (
            select(Participant)
            .where(
                and_(
                    Participant.nomination_id == nomination_id,
                    Participant.scoped_id == scoped_id,
                )
            )
            .options(joinedload(Participant.event), joinedload(Participant.nomination))
            .limit(1)
        )
        participant = await self.session.scalar(query)
        return participant.to_full_dto() if participant else None

    async def paginate_participants(
        self,
        page_number: int,
        participants_per_page: int,
        only_votable: Optional[bool] = None,
        nomination_id: Optional[str] = None,
        user_id: Optional[int] = None,
        search_query: Optional[str] = None,
    ) -> Page[VotingParticipantDTO]:
        query = (
            select(Participant)
            .order_by(Participant.scoped_id)
            .options(undefer(Participant.votes_count))
        )
        if only_votable:
            query = query.where(
                and_(
                    case(
                        (
                            Participant.event.has(),
                            Participant.event.has(Event.skip.isnot(True)),
                        ),
                        else_=True,
                    ),
                    Participant.nomination.has(Nomination.votable.is_(True)),
                ),
            )
        if nomination_id:
            query = query.where(
                Participant.nomination.has(Nomination.id == nomination_id),
            )
        if user_id:
            query = query.options(contains_eager(Participant.user_vote)).outerjoin(
                Vote,
                and_(
                    Vote.participant_id == Participant.id,
                    Vote.user_id == user_id,
                ),
            )
        if search_query:
            query = query.where(Participant.title.ilike(f"%{search_query}%"))
        page = await super()._paginate(query, page_number, participants_per_page)
        return Page(
            items=[p.to_voting_dto() for p in page.items],
            number=page.number,
            total_pages=page.total_pages,
        )
