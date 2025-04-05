from sqlalchemy import Select, and_, case, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager, joinedload, undefer

from fanfan.adapters.db.models import EventORM, NominationORM, ParticipantORM, VoteORM
from fanfan.core.dto.page import Pagination
from fanfan.core.models.nomination import NominationId
from fanfan.core.models.participant import (
    Participant,
    ParticipantFull,
    ParticipantId,
    ParticipantVotingNumber,
)
from fanfan.core.models.user import UserId


class ParticipantsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _filter_participants_query(
        query: Select,
        nomination_id: NominationId | None = None,
        search_query: str | None = None,
        only_votable: bool | None = None,
    ) -> Select:
        if nomination_id:
            query = query.where(
                ParticipantORM.nomination.has(NominationORM.id == nomination_id),
            )
        if search_query:
            query = query.where(
                or_(
                    ParticipantORM.title.ilike(f"%{search_query}%"),
                    ParticipantORM.voting_number == int(search_query)
                    if search_query.isnumeric()
                    else False,
                )
            )
        if only_votable:
            query = query.where(
                and_(
                    case(
                        (
                            ParticipantORM.event.has(),
                            ParticipantORM.event.has(EventORM.is_skipped.isnot(True)),
                        ),
                        else_=True,
                    ),
                    ParticipantORM.nomination.has(NominationORM.is_votable.is_(True)),
                ),
            )
        return query

    @staticmethod
    def _load_full(query: Select, user_id: UserId | None = None) -> Select:
        query = query.options(
            joinedload(ParticipantORM.nomination),
            joinedload(ParticipantORM.event),
            undefer(ParticipantORM.votes_count),
        )
        if user_id:
            query = query.options(contains_eager(ParticipantORM.user_vote)).outerjoin(
                VoteORM,
                and_(
                    VoteORM.participant_id == ParticipantORM.id,
                    VoteORM.user_id == user_id,
                ),
            )
        return query

    async def save_participant(self, model: Participant) -> Participant:
        participant = await self.session.merge(ParticipantORM.from_model(model))
        await self.session.flush([participant])
        return participant.to_model()

    async def get_participant_by_id(
        self, participant_id: ParticipantId
    ) -> ParticipantFull | None:
        query = select(ParticipantORM).where(ParticipantORM.id == participant_id)
        query = self._load_full(query)
        participant = await self.session.scalar(query)
        return participant.to_full_model() if participant else None

    async def get_participant_by_voting_number(
        self, nomination_id: NominationId, voting_number: ParticipantVotingNumber
    ) -> Participant | None:
        query = (
            select(ParticipantORM)
            .where(
                and_(
                    ParticipantORM.nomination_id == nomination_id,
                    ParticipantORM.voting_number == voting_number,
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
    ) -> list[ParticipantFull]:
        query = select(ParticipantORM).order_by(ParticipantORM.voting_number)
        query = self._load_full(query, user_id)

        if pagination:
            query = query.limit(pagination.limit).offset(pagination.offset)
        query = self._filter_participants_query(
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
        query = select(func.count(ParticipantORM.id))
        query = self._filter_participants_query(
            query, nomination_id, search_query, only_votable
        )
        return await self.session.scalar(query)
