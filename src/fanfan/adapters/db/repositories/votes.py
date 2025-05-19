from sqlalchemy import and_, delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.adapters.db.models import NominationORM, VoteORM
from fanfan.core.models.vote import Vote
from fanfan.core.vo.nomination import NominationId
from fanfan.core.vo.user import UserId
from fanfan.core.vo.vote import VoteId


class VotesRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_vote(self, vote: Vote) -> Vote:
        vote_orm = VoteORM.from_model(vote)
        self.session.add(vote_orm)
        await self.session.flush([vote_orm])
        return vote_orm.to_model()

    async def get_vote(self, vote_id: VoteId) -> Vote | None:
        stmt = select(VoteORM).where(VoteORM.id == vote_id)
        vote_orm = await self.session.scalar(stmt)
        return vote_orm.to_model() if vote_orm else None

    async def get_user_vote_by_nomination(
        self, user_id: UserId, nomination_id: NominationId
    ) -> Vote | None:
        vote_orm = await self.session.scalar(
            select(VoteORM).where(
                and_(
                    VoteORM.user_id == user_id,
                    VoteORM.nomination.has(NominationORM.id == nomination_id),
                ),
            )
        )
        return vote_orm.to_model() if vote_orm else None

    async def count_user_votes(self, user_id: UserId) -> int:
        return await self.session.scalar(
            select(func.count(VoteORM.id)).where(VoteORM.user_id == user_id)
        )

    async def delete_vote(self, vote: Vote):
        await self.session.execute(delete(VoteORM).where(VoteORM.id == vote.id))
