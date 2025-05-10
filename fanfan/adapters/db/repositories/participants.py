from sqlalchemy import Select, String, and_, case, cast, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import undefer

from fanfan.adapters.db.models import (
    NominationORM,
    ParticipantORM,
    ScheduleEventORM,
    VoteORM,
)
from fanfan.core.dto.page import Pagination
from fanfan.core.dto.participant import ParticipantUserDTO
from fanfan.core.models.nomination import NominationId
from fanfan.core.models.participant import (
    Participant,
    ParticipantId,
    ParticipantVotingNumber,
)
from fanfan.core.models.user import UserId


def _select_participant_user_dto(user_id: UserId | None) -> Select:
    return (
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


def _parse_participant_user_dto(
    participant_orm: ParticipantORM, vote_orm: VoteORM | None
) -> ParticipantUserDTO:
    return ParticipantUserDTO(
        id=participant_orm.id,
        title=participant_orm.title,
        voting_number=participant_orm.voting_number,
        vote_id=vote_orm.id if vote_orm else None,
        votes_count=participant_orm.votes_count,
    )


def _filter_participants(
    stmt: Select,
    nomination_id: NominationId | None = None,
    search_query: str | None = None,
    only_votable: bool | None = None,
) -> Select:
    filters = []
    if nomination_id:
        filters.append(ParticipantORM.nomination.has(NominationORM.id == nomination_id))
    if search_query:
        filters.append(
            or_(
                ParticipantORM.title.ilike(f"%{search_query}%"),
                ParticipantORM.voting_number == int(search_query)
                if search_query.isnumeric()
                else False,
            )
        )
    if only_votable:
        filters.append(
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
            )
        )
    return stmt.where(*filters)


class ParticipantsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_participant(self, participant: Participant) -> Participant:
        participant_orm = ParticipantORM.from_model(participant)
        self.session.add(participant_orm)
        await self.session.flush([participant_orm])
        return participant_orm.to_model()

    async def get_participant_by_id(
        self, participant_id: ParticipantId
    ) -> Participant | None:
        stmt = (
            select(ParticipantORM)
            .where(ParticipantORM.id == participant_id)
            .with_for_update()
        )
        participant_orm = await self.session.scalar(stmt)
        return participant_orm.to_model() if participant_orm else None

    async def get_participant_by_voting_number(
        self, nomination_id: NominationId, voting_number: ParticipantVotingNumber
    ) -> Participant | None:
        stmt = select(ParticipantORM).where(
            and_(
                ParticipantORM.nomination_id == nomination_id,
                ParticipantORM.voting_number == voting_number,
            ),
        )
        participant_orm = await self.session.scalar(stmt)
        return participant_orm.to_model() if participant_orm else None

    async def save_participant(self, participant: Participant) -> Participant:
        participant_orm = await self.session.merge(
            ParticipantORM.from_model(participant)
        )
        await self.session.flush([participant_orm])
        return participant_orm.to_model()

    async def read_votable_participants_for_user(
        self,
        user_id: UserId,
        nomination_id: NominationId | None = None,
        search_query: str | None = None,
        pagination: Pagination | None = None,
    ) -> list[ParticipantUserDTO]:
        stmt = _select_participant_user_dto(user_id)

        # Filter
        stmt = _filter_participants(
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
            _parse_participant_user_dto(
                participant_orm=participant_orm, vote_orm=vote_orm
            )
            for participant_orm, vote_orm in result
        ]

    async def count_votable_participants(
        self,
        nomination_id: NominationId | None = None,
        search_query: str | None = None,
    ) -> int:
        stmt = select(func.count(ParticipantORM.id))
        stmt = _filter_participants(
            stmt=stmt,
            nomination_id=nomination_id,
            search_query=search_query,
            only_votable=True,
        )
        return await self.session.scalar(stmt)
