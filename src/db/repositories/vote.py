from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Vote
from .base import Repository


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
        tg_id: int = None,
        participant_id: str = None,
    ) -> Vote:
        new_vote = await self.session.merge(
            Vote(
                tg_id=tg_id,
                participant_id=participant_id,
            )
        )
        return new_vote
