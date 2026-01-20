import logging
from dataclasses import dataclass

from sqlalchemy.exc import IntegrityError

from fanfan.adapters.db.repositories.participants import ParticipantsRepository
from fanfan.adapters.db.repositories.tickets import TicketsRepository
from fanfan.adapters.db.repositories.votes import VotesRepository
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.adapters.nats.events_broker import EventsBroker
from fanfan.application.common.id_provider import IdProvider
from fanfan.core.events.voting import VoteUpdatedEvent
from fanfan.core.exceptions.participants import ParticipantNotFound
from fanfan.core.exceptions.votes import (
    AlreadyVotedInThisNomination,
)
from fanfan.core.models.vote import Vote
from fanfan.core.services.voting import VotingService
from fanfan.core.vo.nomination import NominationId
from fanfan.core.vo.participant import ParticipantVotingNumber

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class AddVoteDTO:
    nomination_id: NominationId
    voting_number: ParticipantVotingNumber


class AddVote:
    def __init__(
        self,
        participants_repo: ParticipantsRepository,
        votes_repo: VotesRepository,
        uow: UnitOfWork,
        service: VotingService,
        id_provider: IdProvider,
        events_broker: EventsBroker,
        tickets_repo: TicketsRepository,
    ) -> None:
        self.participants_repo = participants_repo
        self.votes_repo = votes_repo
        self.uow = uow
        self.service = service
        self.id_provider = id_provider
        self.events_broker = events_broker
        self.tickets_repo = tickets_repo

    async def __call__(
        self,
        data: AddVoteDTO,
    ) -> Vote:
        # Ensure user can even vote
        user = await self.id_provider.get_current_user()
        ticket = await self.tickets_repo.get_ticket_by_user_id(user.id)
        await self.service.ensure_user_can_vote(user=user, ticket=ticket)

        # Checking participant
        participant = await self.participants_repo.get_participant_by_voting_number(
            nomination_id=data.nomination_id, voting_number=data.voting_number
        )
        if not participant:
            raise ParticipantNotFound

        # Check if user voted before in this nomination
        if await self.votes_repo.get_user_vote_by_nomination(
            user.id, data.nomination_id
        ):
            raise AlreadyVotedInThisNomination

        async with self.uow:
            try:
                vote = Vote(user_id=user.id, participant_id=participant.id)
                vote = await self.votes_repo.add_vote(vote)
                await self.uow.commit()
            except IntegrityError as e:
                await self.uow.rollback()
                raise AlreadyVotedInThisNomination from e
            else:
                logger.info(
                    "User %s voted for participant %s",
                    user.id,
                    participant.id,
                    extra={"vote": vote},
                )
                await self.events_broker.publish(VoteUpdatedEvent(vote=vote))
                return vote
