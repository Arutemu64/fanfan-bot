from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager

from fanfan.core.models.nomination import FullNominationModel, NominationId
from fanfan.core.models.page import Pagination
from fanfan.core.models.user import UserId
from fanfan.infrastructure.db.models import Nomination, Participant, Vote


class NominationsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_nomination_by_id(
        self, nomination_id: NominationId, user_id: UserId | None = None
    ) -> FullNominationModel | None:
        query = select(Nomination).where(Nomination.id == nomination_id).limit(1)

        if user_id:
            query = query.options(contains_eager(Nomination.user_vote)).outerjoin(
                Vote,
                and_(
                    Vote.user_id == user_id,
                    Vote.participant.has(Participant.nomination_id == Nomination.id),
                ),
            )

        nomination = await self.session.scalar(query)
        return nomination.to_full_model()

    async def list_nominations(
        self, user_id: UserId | None = None, pagination: Pagination | None = None
    ) -> list[FullNominationModel]:
        query = select(Nomination)

        if pagination:
            query = query.limit(pagination.limit).offset(pagination.offset)

        if user_id:
            query = query.options(contains_eager(Nomination.user_vote)).outerjoin(
                Vote,
                and_(
                    Vote.user_id == user_id,
                    Vote.participant.has(Participant.nomination_id == Nomination.id),
                ),
            )

        nominations = await self.session.scalars(query)

        return [n.to_full_model() for n in nominations]

    async def count_nominations(self) -> int:
        return await self.session.scalar(select(func.count(Nomination.id)))
