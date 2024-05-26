import logging
from typing import Optional

from sqlalchemy.exc import IntegrityError

from fanfan.application.dto.common import Page
from fanfan.application.dto.nomination import FullNominationDTO
from fanfan.application.dto.participant import ParticipantDTO, VotingParticipantDTO
from fanfan.application.dto.vote import CreateVoteDTO, VoteDTO
from fanfan.application.exceptions.nomination import NominationNotFound
from fanfan.application.exceptions.participant import ParticipantNotFound
from fanfan.application.exceptions.users import (
    UserHasNoTicket,
    UserNotFound,
)
from fanfan.application.exceptions.voting import (
    AlreadyVotedInThisNomination,
    VotingDisabled,
)
from fanfan.application.services.access import check_permission
from fanfan.application.services.base import BaseService

logger = logging.getLogger(__name__)


class VotingService(BaseService):
    async def get_nomination(
        self, nomination_id: str, user_id: Optional[int] = None
    ) -> FullNominationDTO:
        """@param nomination_id:
        @raise NominationNotFound
        @return:
        """
        if nomination := await self.uow.nominations.get_nomination(
            nomination_id=nomination_id, user_id=user_id
        ):
            return nomination
        raise NominationNotFound

    async def get_nominations_page(
        self,
        page_number: int,
        nominations_per_page: int,
        user_id: Optional[int] = None,
    ) -> Page[FullNominationDTO]:
        """Get nominations page
        @param page_number: Page page_number
        @param nominations_per_page: Nominations per page
        @param user_id: if provided, Nomination will also include user's vote
        @return:
        """
        return await self.uow.nominations.paginate_nominations(
            page_number=page_number,
            nominations_per_page=nominations_per_page,
            only_votable=True,
            user_id=user_id,
        )

    async def get_participants_page(
        self,
        nomination_id: str,
        page_number: int,
        participants_per_page: int,
        user_id: Optional[int] = None,
        search_query: Optional[str] = None,
    ) -> Page[VotingParticipantDTO]:
        """Get participants page
        @param nomination_id: Nomination ID
        @param page_number: Page page_number
        @param participants_per_page: Participants per page
        @param user_id: if provided, Participant will also include user's vote
        @return:
        """
        return await self.uow.participants.paginate_participants(
            page_number=page_number,
            participants_per_page=participants_per_page,
            only_votable=True,
            nomination_id=nomination_id,
            user_id=user_id,
            search_query=search_query,
        )

    async def get_participant_by_scoped_id(
        self, nomination_id: str, scoped_id: int
    ) -> ParticipantDTO:
        participant = await self.uow.participants.get_participant_by_scoped_id(
            nomination_id=nomination_id,
            scoped_id=scoped_id,
        )
        if participant:
            return participant
        raise ParticipantNotFound

    @check_permission(ticket_required=True)
    async def add_vote(
        self,
        user_id: int,
        nomination_id: str,
        participant_scoped_id: int,
    ) -> VoteDTO:
        # Checking settings
        settings = await self.uow.settings.get_settings()
        if not settings.voting_enabled:
            raise VotingDisabled

        # Checking participant
        participant = await self.uow.participants.get_participant_by_scoped_id(
            nomination_id, participant_scoped_id
        )
        if not participant:
            raise ParticipantNotFound
        if participant.event:
            if participant.event.skip:
                raise ParticipantNotFound

        # Checking user
        user = await self.uow.users.get_user_by_id(user_id)
        if not user:
            raise UserNotFound
        if not user.ticket:
            raise UserHasNoTicket

        # Checking user vote
        if await self.uow.votes.get_vote_by_nomination(
            user_id=user_id, nomination_id=nomination_id
        ):
            raise AlreadyVotedInThisNomination

        async with self.uow:
            try:
                vote = await self.uow.votes.add_vote(
                    CreateVoteDTO(
                        user_id=user_id,
                        participant_id=participant.id,
                    )
                )
                await self.uow.commit()
                logger.info(
                    f"User id={user.id} vote for Participant id={participant.id}"
                )
                return vote
            except IntegrityError:
                await self.uow.rollback()
                raise AlreadyVotedInThisNomination

    async def cancel_vote(self, vote_id: int) -> None:
        async with self.uow:
            await self.uow.votes.delete_vote(vote_id)
            await self.uow.commit()
            logger.info(f"Vote id={vote_id} was cancelled")
