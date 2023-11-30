from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...bot.structures import Page
from ..models import DBUser, Nomination, Participant, Vote
from .abstract import Repository


class NominationRepo(Repository[Nomination]):
    def __init__(self, session: AsyncSession):
        super().__init__(type_model=Nomination, session=session)

    async def new(self, id: str, title: str, votable: bool = True) -> Nomination:
        new_nomination = await self.session.merge(
            Nomination(id=id, title=title, votable=votable)
        )
        return new_nomination

    async def get(self, nomination_id: str) -> Optional[Nomination]:
        return await super()._get(ident=nomination_id)

    async def paginate(
        self, page: int, nominations_per_page: int, votable: Optional[bool] = None
    ) -> Page[Nomination]:
        return await super()._paginate(
            page=page,
            items_per_page=nominations_per_page,
            query=Nomination.votable.is_(votable) if votable is not None else True,
            order_by=Nomination.title,
        )

    async def check_if_user_voted_in_nominations(
        self, user: DBUser, nominations: Sequence[Nomination]
    ) -> Sequence[Nomination]:
        stmt = (
            select(Nomination)
            .where(Nomination.id.in_([x.id for x in nominations]))
            .join(Participant)
            .join(Vote)
            .where(Vote.user == user)
        )
        return (await self.session.scalars(stmt)).all()
