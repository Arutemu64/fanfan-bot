import logging

from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.application.common.id_provider import IdProvider
from fanfan.core.exceptions.access import AccessDenied
from fanfan.core.exceptions.votes import VoteNotFound
from fanfan.infrastructure.db.models import Vote

logger = logging.getLogger(__name__)


class CancelVote:
    def __init__(
        self,
        session: AsyncSession,
        id_provider: IdProvider,
    ) -> None:
        self.session = session
        self.id_provider = id_provider

    async def __call__(self, vote_id: int) -> None:
        async with self.session:
            vote = await self.session.get(Vote, vote_id)
            if vote is None:
                raise VoteNotFound
            if vote.user_id != self.id_provider.get_current_user_id():
                raise AccessDenied
            await self.session.delete(vote)
            await self.session.commit()
