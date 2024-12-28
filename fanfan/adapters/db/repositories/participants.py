from sqlalchemy import Select, and_, case, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager, joinedload, undefer

from fanfan.adapters.db.models import DBEvent, DBNomination, DBParticipant, DBVote
from fanfan.core.dto.page import Pagination
from fanfan.core.models.nomination import NominationId
from fanfan.core.models.participant import (
    FullParticipant,
    Participant,
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
                DBParticipant.nomination.has(DBNomination.id == nomination_id),
            )
        if search_query:
            query = query.where(
                or_(
                    DBParticipant.title.ilike(f"%{search_query}%"),
                    DBParticipant.voting_number == int(search_query)
                    if search_query.isnumeric()
                    else False,
                )
            )
        if only_votable:
            query = query.where(
                and_(
                    case(
                        (
                            DBParticipant.event.has(),
                            DBParticipant.event.has(DBEvent.is_skipped.isnot(True)),
                        ),
                        else_=True,
                    ),
                    DBParticipant.nomination.has(DBNomination.is_votable.is_(True)),
                ),
            )
        return query

    @staticmethod
    def _load_full(query: Select, user_id: UserId | None = None) -> Select:
        query = query.options(
            joinedload(DBParticipant.nomination),
            joinedload(DBParticipant.event),
            undefer(DBParticipant.votes_count),
        )
        if user_id:
            query = query.options(contains_eager(DBParticipant.user_vote)).outerjoin(
                DBVote,
                and_(
                    DBVote.participant_id == DBParticipant.id,
                    DBVote.user_id == user_id,
                ),
            )
        return query

    async def save_participant(self, model: Participant) -> Participant:
        participant = await self.session.merge(DBParticipant.from_model(model))
        await self.session.flush([participant])
        return participant.to_model()

    async def get_participant_by_id(
        self, participant_id: ParticipantId
    ) -> FullParticipant | None:
        query = select(DBParticipant).where(DBParticipant.id == participant_id)
        query = self._load_full(query)
        participant = await self.session.scalar(query)
        return participant.to_full_model() if participant else None

    async def get_participant_by_voting_number(
        self, nomination_id: NominationId, voting_number: ParticipantVotingNumber
    ) -> Participant | None:
        query = (
            select(DBParticipant)
            .where(
                and_(
                    DBParticipant.nomination_id == nomination_id,
                    DBParticipant.voting_number == voting_number,
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
    ) -> list[FullParticipant]:
        query = select(DBParticipant).order_by(DBParticipant.voting_number)
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
        query = select(func.count(DBParticipant.id))
        query = self._filter_participants_query(
            query, nomination_id, search_query, only_votable
        )
        return await self.session.scalar(query)
