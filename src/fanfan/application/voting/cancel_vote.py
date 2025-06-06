import logging
from dataclasses import dataclass

from fanfan.adapters.db.repositories.votes import VotesRepository
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.adapters.utils.events_broker import EventsBroker
from fanfan.application.common.id_provider import IdProvider
from fanfan.core.events.voting import VoteUpdatedEvent
from fanfan.core.exceptions.base import AccessDenied
from fanfan.core.exceptions.votes import VoteNotFound
from fanfan.core.vo.vote import VoteId

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class CancelVoteDTO:
    vote_id: VoteId


class CancelVote:
    def __init__(
        self,
        votes_repo: VotesRepository,
        uow: UnitOfWork,
        id_provider: IdProvider,
        events_broker: EventsBroker,
    ) -> None:
        self.votes_repo = votes_repo
        self.uow = uow
        self.id_provider = id_provider
        self.events_broker = events_broker

    async def __call__(self, data: CancelVoteDTO) -> None:
        vote = await self.votes_repo.get_vote(data.vote_id)
        if vote is None:
            raise VoteNotFound
        if vote.user_id != self.id_provider.get_current_user_id():
            raise AccessDenied
        async with self.uow:
            await self.votes_repo.delete_vote(vote)
            await self.uow.commit()
            logger.info(
                "User %s cancelled their vote for %s",
                vote.user_id,
                vote.participant_id,
                extra={"vote": vote},
            )
            await self.events_broker.publish(VoteUpdatedEvent(vote=vote))
