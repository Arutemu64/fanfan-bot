from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager

from fanfan.adapters.db.models import Nomination, Participant, Vote
from fanfan.core.models.nomination import (
    FullNominationModel,
    NominationId,
    NominationModel,
)
from fanfan.core.models.page import Pagination
from fanfan.core.models.user import UserId


class NominationsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def merge_nomination(self, model: NominationModel) -> NominationModel:
        nomination = Nomination(
            id=model.id, code=model.code, title=model.title, votable=model.votable
        )
        await self.session.merge(nomination)
        await self.session.flush([nomination])
        return nomination.to_model()

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
        self,
        only_votable: bool = False,
        user_id: UserId | None = None,
        pagination: Pagination | None = None,
    ) -> list[FullNominationModel]:
        query = select(Nomination)

        if only_votable:
            query = query.where(Nomination.votable.is_(True))

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

    async def count_nominations(self, only_votable: bool) -> int:
        query = select(func.count(Nomination.id))

        if only_votable:
            query = query.where(Nomination.votable.is_(True))

        return await self.session.scalar(query)