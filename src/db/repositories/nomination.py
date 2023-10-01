from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Nomination
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

    async def get_count(self, votable: Optional[bool] = None) -> int:
        return await super()._get_count(
            query=Nomination.votable.is_(votable) if votable is not None else None
        )

    async def get_pages_count(
        self, nominations_per_page: int, votable: Optional[bool] = None
    ) -> int:
        return await super()._get_pages_count(
            items_per_page=nominations_per_page,
            query=Nomination.votable.is_(votable) if votable is not None else True,
        )

    async def get_page(
        self, page: int, nominations_per_page: int, votable: Optional[bool] = None
    ) -> List[Nomination]:
        return await super()._get_page(
            page=page,
            items_per_page=nominations_per_page,
            query=Nomination.votable.is_(votable) if votable is not None else True,
            order_by=Nomination.title,
        )
