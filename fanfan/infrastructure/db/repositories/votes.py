from typing import Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.infrastructure.db.models import Nomination, Vote
from fanfan.infrastructure.db.repositories.repo import Repository


class VotesRepository(Repository[Vote]):
    def __init__(self, session: AsyncSession):
        self.session = session
        super().__init__(type_model=Vote, session=session)

    async def get_vote(self, vote_id: int) -> Optional[Vote]:
        return await self.session.get(Vote, vote_id)

    async def get_vote_by_nomination(
        self,
        user_id: int,
        nomination_id: str,
    ) -> Optional[Vote]:
        query = select(Vote).where(
            and_(
                Vote.user_id == user_id,
                Vote.nomination.has(Nomination.id == nomination_id),
            ),
        )
        return await self.session.scalar(query)
