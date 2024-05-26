from typing import Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager

from fanfan.application.dto.common import Page
from fanfan.application.dto.nomination import (
    CreateNominationDTO,
    FullNominationDTO,
    NominationDTO,
)
from fanfan.infrastructure.db.models import Nomination, Participant, Vote
from fanfan.infrastructure.db.repositories.repo import Repository


class NominationsRepository(Repository[Nomination]):
    def __init__(self, session: AsyncSession):
        self.session = session
        super().__init__(type_model=Nomination, session=session)

    async def add_nomination(self, dto: CreateNominationDTO) -> NominationDTO:
        nomination = Nomination(**dto.model_dump(exclude_unset=True))
        self.session.add(nomination)
        await self.session.flush([nomination])
        return nomination.to_dto()

    async def get_nomination(
        self, nomination_id: str, user_id: Optional[int] = None
    ) -> Optional[FullNominationDTO]:
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
        return nomination.to_full_dto() if nomination else None

    async def paginate_nominations(
        self,
        page_number: int,
        nominations_per_page: int,
        only_votable: Optional[bool] = None,
        user_id: Optional[int] = None,
    ) -> Page[FullNominationDTO]:
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
        page = await super()._paginate(query, page_number, nominations_per_page)
        return Page(
            items=[n.to_full_dto() for n in page.items],
            number=page.number,
            total_pages=page.total_pages,
        )
