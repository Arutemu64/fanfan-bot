from sqlalchemy import Select, and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager

from fanfan.adapters.db.models import NominationORM, ParticipantORM, VoteORM
from fanfan.core.dto.page import Pagination
from fanfan.core.models.nomination import (
    Nomination,
    NominationFull,
    NominationId,
)
from fanfan.core.models.user import UserId


class NominationsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _filter_nominations(query: Select, only_votable: bool) -> Select:
        if only_votable:
            query = query.where(NominationORM.is_votable.is_(True))
        return query

    @staticmethod
    def _load_full(query: Select, user_id: UserId | None = None) -> Select:
        if user_id:
            query = query.options(contains_eager(NominationORM.user_vote)).outerjoin(
                VoteORM,
                and_(
                    VoteORM.user_id == user_id,
                    VoteORM.participant.has(
                        ParticipantORM.nomination_id == NominationORM.id
                    ),
                ),
            )
        return query

    async def save_nomination(self, model: Nomination) -> Nomination:
        nomination = await self.session.merge(NominationORM.from_model(model))
        await self.session.flush([nomination])
        return nomination.to_model()

    async def get_nomination_by_id(
        self, nomination_id: NominationId, user_id: UserId | None = None
    ) -> NominationFull | None:
        query = select(NominationORM).where(NominationORM.id == nomination_id).limit(1)
        query = self._load_full(query, user_id)
        nomination = await self.session.scalar(query)
        return nomination.to_full_model()

    async def list_nominations(
        self,
        only_votable: bool,
        user_id: UserId | None = None,
        pagination: Pagination | None = None,
    ) -> list[NominationFull]:
        query = select(NominationORM)
        query = self._load_full(query, user_id)

        if pagination:
            query = query.limit(pagination.limit).offset(pagination.offset)
        query = self._filter_nominations(query, only_votable)

        nominations = await self.session.scalars(query)
        return [n.to_full_model() for n in nominations]

    async def count_nominations(self, only_votable: bool) -> int:
        query = select(func.count(NominationORM.id))
        query = self._filter_nominations(query, only_votable)
        return await self.session.scalar(query)
