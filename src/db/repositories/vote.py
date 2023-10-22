from typing import Optional

from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Nomination, Participant, User, Vote
from .abstract import Repository


class VoteRepo(Repository[Vote]):
    def __init__(self, session: AsyncSession):
        super().__init__(type_model=Vote, session=session)

    async def new(
        self,
        user: User,
        participant: Participant,
    ) -> Vote:
        new_vote = await self.session.merge(
            Vote(
                user=user,
                participant=participant,
            )
        )
        return new_vote

    async def get(self, vote_id: int) -> Optional[Vote]:
        return await super()._get(vote_id)

    async def get_user_vote_by_nomination(
        self, user: User, nomination: Nomination
    ) -> Optional[Vote]:
        query = and_(
            Vote.user == user,
            Vote.participant.has(Participant.nomination == nomination),
        )
        return await super()._get_by_where(query)
