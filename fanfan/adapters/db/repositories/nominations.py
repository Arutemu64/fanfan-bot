from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.adapters.db.models import NominationORM, ParticipantORM, VoteORM
from fanfan.core.dto.nomination import UserNominationDTO
from fanfan.core.dto.page import Pagination
from fanfan.core.models.nomination import (
    Nomination,
    NominationId,
)
from fanfan.core.models.user import UserId


class NominationsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _to_user_dto(
        nomination: NominationORM, vote: VoteORM | None
    ) -> UserNominationDTO:
        return UserNominationDTO(
            id=nomination.id,
            title=nomination.title,
            vote=vote.to_model() if vote else None,
        )

    async def save_nomination(self, nomination: Nomination) -> Nomination:
        nomination_orm = await self.session.merge(NominationORM.from_model(nomination))
        await self.session.flush([nomination_orm])
        return nomination_orm.to_model()

    async def read_nomination_for_user(
        self, nomination_id: NominationId, user_id: UserId
    ) -> UserNominationDTO | None:
        stmt = (
            select(NominationORM, VoteORM)
            .where(NominationORM.id == nomination_id)
            .outerjoin(
                VoteORM,
                and_(
                    VoteORM.user_id == user_id,
                    VoteORM.participant.has(
                        ParticipantORM.nomination_id == NominationORM.id
                    ),
                ),
            )
        )

        result = (await self.session.execute(stmt)).first()
        nomination_orm, vote_orm = result

        return (
            self._to_user_dto(nomination=nomination_orm, vote=vote_orm)
            if result
            else None
        )

    async def read_votable_nominations_list_for_user(
        self,
        user_id: UserId,
        pagination: Pagination | None = None,
    ) -> list[UserNominationDTO]:
        stmt = (
            select(NominationORM, VoteORM)
            .where(NominationORM.is_votable.is_(True))
            .outerjoin(
                VoteORM,
                and_(
                    VoteORM.user_id == user_id,
                    VoteORM.participant.has(
                        ParticipantORM.nomination_id == NominationORM.id
                    ),
                ),
            )
        )

        if pagination:
            stmt = stmt.limit(pagination.limit).offset(pagination.offset)

        results = (await self.session.execute(stmt)).all()

        return [
            self._to_user_dto(nomination=nomination_orm, vote=vote_orm)
            for nomination_orm, vote_orm in results
        ]

    async def count_votable_nominations(self) -> int:
        stmt = select(func.count(NominationORM.id)).where(
            NominationORM.is_votable.is_(True)
        )
        return await self.session.scalar(stmt)
