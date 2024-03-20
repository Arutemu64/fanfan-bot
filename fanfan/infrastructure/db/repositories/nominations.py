from typing import Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager

from fanfan.application.dto.common import Page
from fanfan.infrastructure.db.models import Nomination, Participant, Vote
from fanfan.infrastructure.db.repositories.repo import Repository


class NominationsRepository(Repository[Nomination]):
    def __init__(self, session: AsyncSession):
        self.session = session
        super().__init__(type_model=Nomination, session=session)

    async def get_nomination(self, nomination_id: str) -> Optional[Nomination]:
        return await self.session.get(Nomination, nomination_id)

    async def paginate_nominations(
        self,
        page_number: int,
        nominations_per_page: int,
        only_votable: Optional[bool] = None,
        user_id: Optional[int] = None,
    ) -> Page[Nomination]:
        query = select(Nomination)
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
        return await super()._paginate(query, page_number, nominations_per_page)
