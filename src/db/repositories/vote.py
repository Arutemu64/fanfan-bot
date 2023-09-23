from typing import Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Participant, Vote
from .abstract import Repository


class VoteRepo(Repository[Vote]):
    """
    User repository for CRUD and other SQL queries
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize user repository as for all users or only for one user
        """
        super().__init__(type_model=Vote, session=session)

    async def new(
        self,
        user_id: int = None,
        participant_id: str = None,
    ) -> Vote:
        new_vote = await self.session.merge(
            Vote(
                user_id=user_id,
                participant_id=participant_id,
            )
        )
        return new_vote

    async def check_vote(
        self,
        user_id: int,
        nomination_id: str = None,
        participant_id: int = None,
    ) -> Optional[Vote]:
        terms = [(Vote.user_id == user_id)]
        if nomination_id:
            terms.append(
                Vote.participant.has(Participant.nomination_id == nomination_id)
            )
        elif participant_id:
            terms.append(Vote.participant_id == participant_id)
        return (
            await self.session.execute(select(Vote).where(and_(*terms)).limit(1))
        ).scalar_one_or_none()
