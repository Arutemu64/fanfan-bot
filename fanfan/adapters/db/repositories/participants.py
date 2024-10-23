from sqlalchemy import Select, and_, case, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager, joinedload, undefer

from fanfan.adapters.db.models import Event, Nomination, Participant, Vote
from fanfan.core.models.nomination import NominationId
from fanfan.core.models.page import Pagination
from fanfan.core.models.participant import (
    FullParticipantModel,
    ParticipantId,
    ParticipantModel,
    ParticipantScopedId,
)
from fanfan.core.models.user import UserId


def _filter_participants_query(
    query: Select,
    nomination_id: NominationId | None = None,
    search_query: str | None = None,
    only_votable: bool | None = None,
) -> Select:
    if nomination_id:
        query = query.where(
            Participant.nomination.has(Nomination.id == nomination_id),
        )
    if search_query:
        query = query.where(
            or_(
                Participant.title.ilike(f"%{search_query}%"),
                Participant.scoped_id == int(search_query)
                if search_query.isnumeric()
                else False,
            )
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
    return query


class ParticipantsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def merge_participant(self, model: ParticipantModel) -> ParticipantModel:
        participant = Participant.from_model(model)
        await self.session.merge(participant)
        await self.session.flush([participant])
        return participant.to_model()

    async def get_participant_by_id(
        self, participant_id: ParticipantId
    ) -> FullParticipantModel | None:
        participant = await self.session.get(
            Participant,
            participant_id,
            options=[
                joinedload(Participant.nomination),
                joinedload(Participant.event),
                undefer(Participant.votes_count),
            ],
        )
        return participant.to_full_model() if participant else None

    async def get_participant_by_scoped_id(
        self, nomination_id: NominationId, scoped_id: ParticipantScopedId
    ) -> ParticipantModel | None:
        query = (
            select(Participant)
            .where(
                and_(
                    Participant.nomination_id == nomination_id,
                    Participant.scoped_id == scoped_id,
                ),
            )
            .limit(1)
        )
        participant = await self.session.scalar(query)
        return participant.to_model() if participant else None

    async def list_participants(
        self,
        only_votable: bool,
        nomination_id: NominationId | None = None,
        search_query: str | None = None,
        user_id: UserId | None = None,
        pagination: Pagination | None = None,
    ) -> list[FullParticipantModel]:
        query = (
            select(Participant)
            .order_by(Participant.scoped_id)
            .options(
                joinedload(Participant.event),
                joinedload(Participant.nomination),
                undefer(Participant.votes_count),
            )
        )
        if pagination:
            query = query.limit(pagination.limit).offset(pagination.offset)
        if user_id:
            query = query.options(contains_eager(Participant.user_vote)).outerjoin(
                Vote,
                and_(
                    Vote.participant_id == Participant.id,
                    Vote.user_id == user_id,
                ),
            )

        query = _filter_participants_query(
            query, nomination_id, search_query, only_votable
        )

        participants = await self.session.scalars(query)

        return [p.to_full_model() for p in participants]

    async def count_participants(
        self,
        only_votable: bool,
        nomination_id: NominationId | None = None,
        search_query: str | None = None,
    ) -> int:
        query = select(func.count(Participant.id))

        query = _filter_participants_query(
            query, nomination_id, search_query, only_votable
        )

        return await self.session.scalar(query)
