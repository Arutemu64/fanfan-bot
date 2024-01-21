from typing import Optional, Sequence

from sqlalchemy import Select, and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager, joinedload

from fanfan.infrastructure.db.models import Event, Nomination, Participant, Vote
from fanfan.infrastructure.db.repositories.repo import Repository


def _build_participants_query(
    query: Select,
    only_votable: Optional[bool] = None,
    nomination_id: Optional[str] = None,
    user_id: Optional[int] = None,
) -> Select:
    if only_votable:
        query = query.where(
            and_(
                Participant.nomination.has(Nomination.votable.is_(True)),
                Participant.event.has(Event.skip.isnot(True)),
            )
        )
    if nomination_id:
        query = query.where(Participant.nomination.has(Nomination.id == nomination_id))
    if user_id:
        query = query.options(contains_eager(Participant.user_vote)).outerjoin(
            Vote,
            and_(
                Vote.participant_id == Participant.id,
                Vote.user_id == user_id,
            ),
        )
    return query


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
        page: int,
        participants_per_page: int,
        only_votable: Optional[bool] = None,
        nomination_id: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> Sequence[Participant]:
        query = _build_participants_query(
            select(Participant),
            only_votable=only_votable,
            nomination_id=nomination_id,
            user_id=user_id,
        )
        query = query.slice(
            start=page * participants_per_page,
            stop=(page * participants_per_page) + participants_per_page,
        )
        return (await self.session.scalars(query)).all()

    async def count_participants(
        self,
        only_votable: Optional[bool] = None,
        nomination_id: Optional[str] = None,
    ) -> int:
        query = _build_participants_query(
            select(func.count(Participant.id)),
            only_votable=only_votable,
            nomination_id=nomination_id,
        )
        return await self.session.scalar(query)
