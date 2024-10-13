from sqlalchemy import and_, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.core.models.nomination import NominationId
from fanfan.core.models.user import UserId
from fanfan.core.models.vote import VoteId, VoteModel
from fanfan.infrastructure.db.models import Nomination, Vote


class VotesRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_vote(self, model: VoteModel) -> VoteModel:
        vote = Vote(user_id=model.user_id, participant_id=model.participant_id)
        self.session.add(vote)
        await self.session.flush([vote])
        return vote.to_model()

    async def get_vote(self, vote_id: VoteId) -> VoteModel | None:
        vote = await self.session.get(Vote, vote_id)
        return vote.to_model() if vote else None

    async def get_user_vote_by_nomination(
        self, user_id: UserId, nomination_id: NominationId
    ) -> VoteModel | None:
        vote = await self.session.scalar(
            select(Vote).where(
                and_(
                    Vote.user_id == user_id,
                    Vote.nomination.has(Nomination.id == nomination_id),
                ),
            )
        )
        return vote.to_model() if vote else None

    async def delete_vote(self, vote_id: VoteId):
        await self.session.execute(delete(Vote).where(Vote.id == vote_id))
