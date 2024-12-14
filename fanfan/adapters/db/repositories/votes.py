from sqlalchemy import and_, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.adapters.db.models import DBNomination, DBVote
from fanfan.core.models.nomination import NominationId
from fanfan.core.models.user import UserId
from fanfan.core.models.vote import Vote, VoteId


class VotesRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_vote(self, model: Vote) -> Vote:
        vote = DBVote.from_model(model)
        self.session.add(vote)
        await self.session.flush([vote])
        return vote.to_model()

    async def get_vote(self, vote_id: VoteId) -> Vote | None:
        vote = await self.session.get(DBVote, vote_id)
        return vote.to_model() if vote else None

    async def get_user_vote_by_nomination(
        self, user_id: UserId, nomination_id: NominationId
    ) -> Vote | None:
        vote = await self.session.scalar(
            select(DBVote).where(
                and_(
                    DBVote.user_id == user_id,
                    DBVote.nomination.has(DBNomination.id == nomination_id),
                ),
            )
        )
        return vote.to_model() if vote else None

    async def delete_vote(self, vote_id: VoteId):
        await self.session.execute(delete(DBVote).where(DBVote.id == vote_id))
