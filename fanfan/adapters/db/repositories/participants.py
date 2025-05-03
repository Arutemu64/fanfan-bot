from sqlalchemy import Select, String, and_, case, cast, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, undefer

from fanfan.adapters.db.models import (
    NominationORM,
    ParticipantORM,
    ScheduleEventORM,
    VoteORM,
)
from fanfan.core.dto.page import Pagination
from fanfan.core.dto.participant import UserParticipantDTO
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
    def _to_user_dto(participant: ParticipantORM, vote: VoteORM) -> UserParticipantDTO:
        return UserParticipantDTO(
            title=participant.title,
            voting_number=participant.voting_number,
            vote=vote.to_model() if vote else None,
            votes_count=participant.votes_count,
        )

    @staticmethod
    def _filter_participants_query(
        stmt: Select,
        nomination_id: NominationId | None = None,
        search_query: str | None = None,
        only_votable: bool | None = None,
    ) -> Select:
        if nomination_id:
            stmt = stmt.where(
                ParticipantORM.nomination.has(NominationORM.id == nomination_id),
            )
        if search_query:
            stmt = stmt.where(
                or_(
                    ParticipantORM.title.ilike(f"%{search_query}%"),
                    ParticipantORM.voting_number == int(search_query)
                    if search_query.isnumeric()
                    else False,
                )
            )
        if only_votable:
            stmt = stmt.where(
                and_(
                    case(
                        (
                            ParticipantORM.event.has(),
                            ParticipantORM.event.has(
                                ScheduleEventORM.is_skipped.isnot(True)
                            ),
                        ),
                        else_=True,
                    ),
                    ParticipantORM.nomination.has(NominationORM.is_votable.is_(True)),
                ),
            )
        return stmt

    @staticmethod
    def _load_full(stmt: Select) -> Select:
        return stmt.options(
            joinedload(ParticipantORM.nomination),
            joinedload(ParticipantORM.event),
            undefer(ParticipantORM.votes_count),
        )

    async def save_participant(self, participant: Participant) -> Participant:
        participant_orm = await self.session.merge(
            ParticipantORM.from_model(participant)
        )
        await self.session.flush([participant_orm])
        return participant_orm.to_model()

    async def get_participant_by_id(
        self, participant_id: ParticipantId
    ) -> Participant | None:
        stmt = select(ParticipantORM).where(ParticipantORM.id == participant_id)
        participant_orm = await self.session.scalar(stmt)
        return participant_orm.to_model() if participant_orm else None

    async def get_participant_by_voting_number(
        self, nomination_id: NominationId, voting_number: ParticipantVotingNumber
    ) -> ParticipantFull | None:
        stmt = (
            select(ParticipantORM)
            .where(
                and_(
                    ParticipantORM.nomination_id == nomination_id,
                    ParticipantORM.voting_number == voting_number,
                ),
            )
            .limit(1)
        )
        stmt = self._load_full(stmt)
        participant_orm = await self.session.scalar(stmt)
        return participant_orm.to_full_model() if participant_orm else None

    async def read_votable_participants_list_for_user(
        self,
        user_id: UserId,
        nomination_id: NominationId | None = None,
        search_query: str | None = None,
        pagination: Pagination | None = None,
    ) -> list[UserParticipantDTO]:
        stmt = (
            select(ParticipantORM, VoteORM)
            .outerjoin(
                VoteORM,
                and_(
                    VoteORM.participant_id == ParticipantORM.id,
                    VoteORM.user_id == user_id,
                ),
            )
            .options(undefer(ParticipantORM.votes_count))
        )

        # Filter
        stmt = self._filter_participants_query(
            stmt=stmt,
            nomination_id=nomination_id,
            search_query=search_query,
            only_votable=True,
        )

        # Order
        user_unique_order = func.md5(
            func.concat(cast(user_id, String), "-", cast(ParticipantORM.id, String))
        )
        stmt = stmt.order_by(user_unique_order)

        # Limit
        if pagination:
            stmt = stmt.limit(pagination.limit).offset(pagination.offset)

        result = (await self.session.execute(stmt)).all()

        return [
            self._to_user_dto(participant=participant_orm, vote=vote_orm)
            for participant_orm, vote_orm in result
        ]

    async def count_votable_participants(
        self,
        nomination_id: NominationId | None = None,
        search_query: str | None = None,
    ) -> int:
        stmt = select(func.count(ParticipantORM.id))
        stmt = self._filter_participants_query(
            stmt=stmt,
            nomination_id=nomination_id,
            search_query=search_query,
            only_votable=True,
        )
        return await self.session.scalar(stmt)
