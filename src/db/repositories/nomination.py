from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...bot.structures import Page
from ..models import Nomination, Participant, User, Vote
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

    async def get_user_voted_nominations(self, user: User) -> List[Nomination]:
        stmt = select(Nomination).join(Participant).join(Vote).where(Vote.user == user)
        return (await self.session.scalars(stmt)).all()
