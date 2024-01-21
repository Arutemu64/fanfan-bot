from typing import Optional, Sequence

from sqlalchemy import Select, and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager

from fanfan.infrastructure.db.models import Nomination, Participant, Vote
from fanfan.infrastructure.db.repositories.repo import Repository


def _build_nominations_query(
    query: Select, only_votable: Optional[bool] = None, user_id: Optional[int] = None
) -> Select:
    if only_votable:
        query = query.where(Nomination.votable.is_(True))
    if user_id:
        query = query.options(contains_eager(Nomination.user_vote)).outerjoin(
            Vote,
            and_(
                Vote.user_id == user_id,
                Vote.participant.has(Participant.nomination_id == Nomination.id),
            ),
        )
    return query


class NominationsRepository(Repository[Nomination]):
    def __init__(self, session: AsyncSession):
        self.session = session
        super().__init__(type_model=Nomination, session=session)

    async def get_nomination(self, nomination_id: str) -> Optional[Nomination]:
        return await self.session.get(Nomination, nomination_id)

    async def paginate_nominations(
        self,
        page: int,
        nominations_per_page: int,
        only_votable: Optional[bool] = None,
        user_id: Optional[int] = None,
    ) -> Sequence[Nomination]:
        query = _build_nominations_query(
            select(Nomination), only_votable=only_votable, user_id=user_id
        )
        query = query.slice(
            start=page * nominations_per_page,
            stop=(page * nominations_per_page) + nominations_per_page,
        )
        return (await self.session.scalars(query)).all()

    async def count_nominations(self, only_votable: Optional[bool] = None) -> int:
        query = _build_nominations_query(
            select(func.count(Nomination.id)), only_votable=only_votable
        )
        return await self.session.scalar(query)
