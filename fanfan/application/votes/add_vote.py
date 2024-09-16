import logging

from sqlalchemy import and_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from fanfan.application.common.id_provider import IdProvider
from fanfan.core.exceptions.participants import ParticipantNotFound
from fanfan.core.exceptions.users import TicketNotLinked, UserNotFound
from fanfan.core.exceptions.votes import (
    AlreadyVotedInThisNomination,
    VotingDisabled,
)
from fanfan.core.models.vote import VoteDTO
from fanfan.infrastructure.db.models import (
    Nomination,
    Participant,
    Settings,
    User,
    Vote,
)

logger = logging.getLogger(__name__)


class AddVote:
    def __init__(
        self,
        session: AsyncSession,
        id_provider: IdProvider,
    ) -> None:
        self.session = session
        self.id_provider = id_provider

    async def __call__(
        self,
        participant_id: int,
    ) -> VoteDTO:
        # Checking settings
        settings = await self.session.get(Settings, 1)
        if not settings.voting_enabled:
            raise VotingDisabled

        # Checking user
        user = await self.session.get(
            User,
            self.id_provider.get_current_user_id(),
            options=[joinedload(User.ticket)],
        )
        if not user:
            raise UserNotFound
        if not user.ticket:
            raise TicketNotLinked

        # Checking participant
        participant = await self.session.get(
            Participant, participant_id, options=[joinedload(Participant.event)]
        )
        if not participant:
            raise ParticipantNotFound
        if participant.event and participant.event.skip:
            raise ParticipantNotFound

        # Checking user vote in this nomination
        if await self.session.scalar(
            select(Vote).where(
                and_(
                    Vote.user_id == user.id,
                    Vote.nomination.has(Nomination.id == participant.nomination_id),
                ),
            )
        ):
            raise AlreadyVotedInThisNomination

        async with self.session:
            try:
                vote = Vote(user=user, participant=participant)
                self.session.add(vote)
                await self.session.commit()
                logger.info(
                    "User %s voted for participant %s",
                    user.id,
                    participant.id,
                )
                return vote.to_dto()
            except IntegrityError as e:
                await self.session.rollback()
                raise AlreadyVotedInThisNomination from e
