from typing import Optional

from sqlalchemy import and_, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.application.dto.vote import CreateVoteDTO, VoteDTO
from fanfan.infrastructure.db.models import Nomination, Vote
from fanfan.infrastructure.db.repositories.repo import Repository


class VotesRepository(Repository[Vote]):
    def __init__(self, session: AsyncSession):
        self.session = session
        super().__init__(type_model=Vote, session=session)

    async def add_vote(self, dto: CreateVoteDTO) -> VoteDTO:
        vote = Vote(**dto.model_dump())
        self.session.add(vote)
        await self.session.flush([vote])
        return vote.to_dto()

    async def get_vote(self, vote_id: int) -> Optional[VoteDTO]:
        vote = await self.session.get(Vote, vote_id)
        return vote.to_dto() if vote else None

    async def get_vote_by_nomination(
        self,
        user_id: int,
        nomination_id: str,
    ) -> Optional[VoteDTO]:
        query = select(Vote).where(
            and_(
                Vote.user_id == user_id,
                Vote.nomination.has(Nomination.id == nomination_id),
            ),
        )
        vote = await self.session.scalar(query)
        return vote.to_dto() if vote else None

    async def delete_vote(self, vote_id: int) -> None:
        await self.session.execute(delete(Vote).where(Vote.id == vote_id))
