import logging
from dataclasses import dataclass

from sqlalchemy.exc import IntegrityError

from fanfan.adapters.db.repositories.participants import (
    ParticipantsRepository,
)
from fanfan.adapters.db.repositories.votes import VotesRepository
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.application.common.id_provider import IdProvider
from fanfan.application.common.interactor import Interactor
from fanfan.core.exceptions.participants import ParticipantNotFound
from fanfan.core.exceptions.votes import (
    AlreadyVotedInThisNomination,
)
from fanfan.core.models.participant import ParticipantId
from fanfan.core.models.vote import Vote
from fanfan.core.services.access import AccessService

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class AddVoteDTO:
    participant_id: ParticipantId


class AddVote(Interactor[ParticipantId, Vote]):
    def __init__(
        self,
        participants_repo: ParticipantsRepository,
        votes_repo: VotesRepository,
        uow: UnitOfWork,
        access: AccessService,
        id_provider: IdProvider,
    ) -> None:
        self.participants_repo = participants_repo
        self.votes_repo = votes_repo
        self.uow = uow
        self.access = access
        self.id_provider = id_provider

    async def __call__(
        self,
        participant_id: ParticipantId,
    ) -> Vote:
        # Checking participant
        participant = await self.participants_repo.get_participant_by_id(participant_id)
        if not participant:
            raise ParticipantNotFound
        if participant.event and participant.event.is_skipped:
            raise ParticipantNotFound

        # Checking user
        user = await self.id_provider.get_current_user()
        await self.access.ensure_can_vote(user, participant.nomination_id)

        async with self.uow:
            try:
                vote = await self.votes_repo.add_vote(
                    Vote(user_id=user.id, participant_id=participant_id)
                )
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
                return vote
