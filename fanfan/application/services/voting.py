import logging
from typing import Optional

from fanfan.application.dto.common import Page
from fanfan.application.dto.nomination import NominationDTO, VotingNominationDTO
from fanfan.application.dto.participant import VotingParticipantDTO
from fanfan.application.dto.vote import VoteDTO
from fanfan.application.exceptions.nomination import NominationNotFound
from fanfan.application.exceptions.participant import ParticipantNotFound
from fanfan.application.exceptions.users import (
    UserHasNoTicket,
    UserNotFound,
)
from fanfan.application.exceptions.voting import (
    AlreadyVotedInThisNomination,
    VoteNotFound,
    VotingDisabled,
)
from fanfan.application.services.access import check_permission
from fanfan.application.services.base import BaseService
from fanfan.infrastructure.db.models import Participant, User, Vote

logger = logging.getLogger(__name__)


class VotingService(BaseService):
    async def _check_vote_ability(
        self,
        user: User,
        participant: Participant,
        allowed_nomination_id: Optional[str] = None,
    ) -> None:
        if not user.ticket:
            raise UserHasNoTicket
        settings = await self.uow.settings.get_settings()
        if not settings.voting_enabled:
            raise VotingDisabled
        if participant.event:
            if participant.event.skip:
                raise ParticipantNotFound
        if allowed_nomination_id:
            if participant.nomination_id != allowed_nomination_id:
                raise ParticipantNotFound

    async def get_nomination(self, nomination_id: str) -> NominationDTO:
        """@param nomination_id:
        @raise NominationNotFound
        @return:
        """
        if nomination := await self.uow.nominations.get_nomination(nomination_id):
            return nomination.to_dto()
        raise NominationNotFound

    async def get_nominations_page(
        self,
        page_number: int,
        nominations_per_page: int,
        user_id: Optional[int] = None,
    ) -> Page[VotingNominationDTO]:
        """Get nominations page
        @param page_number: Page page_number
        @param nominations_per_page: Nominations per page
        @param user_id: if provided, Nomination will also include user's vote
        @return:
        """
        page = await self.uow.nominations.paginate_nominations(
            page_number=page_number,
            nominations_per_page=nominations_per_page,
            only_votable=True,
            user_id=user_id,
        )
        return Page(
            items=[n.to_voting_dto() for n in page.items],
            number=page.number,
            total_pages=page.total_pages,
        )

    async def get_participants_page(
        self,
        nomination_id: str,
        page_number: int,
        participants_per_page: int,
        user_id: Optional[int] = None,
    ) -> Page[VotingParticipantDTO]:
        """Get participants page
        @param nomination_id: Nomination ID
        @param page_number: Page page_number
        @param participants_per_page: Participants per page
        @param user_id: if provided, Participant will also include user's vote
        @return:
        """
        page = await self.uow.participants.paginate_participants(
            page_number=page_number,
            participants_per_page=participants_per_page,
            only_votable=True,
            nomination_id=nomination_id,
            user_id=user_id,
        )
        return Page(
            items=[p.to_voting_dto() for p in page.items],
            number=page.number,
            total_pages=page.total_pages,
        )

    @check_permission(ticket_required=True)
    async def add_vote(
        self,
        user_id: int,
        participant_id: int,
        nomination_id: Optional[str] = None,
    ) -> VoteDTO:
        user = await self.uow.users.get_user_by_id(user_id)
        if not user:
            raise UserNotFound
        participant = await self.uow.participants.get_participant(participant_id)
        if not participant:
            raise ParticipantNotFound

        await self._check_vote_ability(user, participant, nomination_id)

        if await self.uow.votes.get_vote_by_nomination(
            user_id=user_id,
            nomination_id=nomination_id,
        ):
            raise AlreadyVotedInThisNomination

        async with self.uow:
            vote = Vote(user_id=user_id, participant_id=participant_id)
            self.uow.session.add(vote)
            await self.uow.commit()
            logger.info(f"User id={user.id} vote for Participant id={participant.id}")
            return vote.to_dto()

    async def get_vote_by_nomination(self, user_id: int, nomination_id: str) -> VoteDTO:
        user_vote = await self.uow.votes.get_vote_by_nomination(
            user_id=user_id,
            nomination_id=nomination_id,
        )
        if not user_vote:
            raise VoteNotFound
        return user_vote.to_dto()

    async def cancel_vote(self, vote_id: int) -> None:
        vote = await self.uow.votes.get_vote(vote_id)
        if not vote:
            raise VoteNotFound
        async with self.uow:
            await self.uow.session.delete(vote)
            logger.info(f"Vote id={vote.id} was cancelled")
            await self.uow.commit()
