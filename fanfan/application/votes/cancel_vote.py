import logging

from fanfan.adapters.db.repositories.votes import VotesRepository
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.application.common.id_provider import IdProvider
from fanfan.application.common.interactor import Interactor
from fanfan.core.exceptions.access import AccessDenied
from fanfan.core.exceptions.votes import VoteNotFound
from fanfan.core.models.vote import VoteId

logger = logging.getLogger(__name__)


class CancelVote(Interactor[VoteId, None]):
    def __init__(
        self,
        votes_repo: VotesRepository,
        uow: UnitOfWork,
        id_provider: IdProvider,
    ) -> None:
        self.votes_repo = votes_repo
        self.uow = uow
        self.id_provider = id_provider

    async def __call__(self, vote_id: VoteId) -> None:
        vote = await self.votes_repo.get_vote(vote_id)
        if vote is None:
            raise VoteNotFound
        if vote.user_id != self.id_provider.get_current_user_id():
            raise AccessDenied
        async with self.uow:
            await self.votes_repo.delete_vote(vote.id)
            await self.uow.commit()
            logger.info(
                "User %s cancelled their vote for %s",
                vote.user_id,
                vote.participant_id,
                extra={"vote": vote},
            )
