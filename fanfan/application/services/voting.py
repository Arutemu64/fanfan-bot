import math
from typing import Optional

from fanfan.application.dto.common import Page
from fanfan.application.dto.vote import VoteDTO
from fanfan.application.exceptions.participant import ParticipantNotFound
from fanfan.application.exceptions.users import (
    UserHasNoTicket,
    UserNotFound,
)
from fanfan.application.exceptions.voting import (
    AlreadyVotedInThisNomination,
    VoteNotFound,
    VotingServiceDisabled,
)
from fanfan.application.services.access import check_permission
from fanfan.application.services.base import BaseService
from fanfan.infrastructure.db.models import Nomination, Participant, User, Vote


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
            raise VotingServiceDisabled
        if participant.event:
            if participant.event.skip:
                raise ParticipantNotFound
        if allowed_nomination_id:
            if participant.nomination_id != allowed_nomination_id:
                raise ParticipantNotFound

    async def get_nominations_page(
        self, page: int, nominations_per_page: int, user_id: Optional[int] = None
    ) -> Page[Nomination]:
        """
        Get nominations page
        @param page: Page number
        @param nominations_per_page: Nominations per page
        @param user_id: if provided, Nomination will also include user's vote
        @return:
        """
        nominations = await self.uow.nominations.paginate_nominations(
            page=page,
            nominations_per_page=nominations_per_page,
            only_votable=True,
            user_id=user_id,
        )
        nominations_count = await self.uow.nominations.count_nominations(
            only_votable=True
        )
        total = math.ceil(nominations_count / nominations_per_page)
        return Page(
            items=nominations,
            number=page,
            total=total if total > 0 else 1,
        )

    async def get_participants_page(
        self,
        nomination_id: str,
        page: int,
        participants_per_page: int,
        user_id: Optional[int] = None,
    ) -> Page[Participant]:
        """
        Get participants page
        @param nomination_id: Nomination ID
        @param page: Page number
        @param participants_per_page: Participants per page
        @param user_id: if provided, Participant will also include user's vote
        @return:
        """
        participants = await self.uow.participants.paginate_participants(
            page=page,
            participants_per_page=participants_per_page,
            only_votable=True,
            nomination_id=nomination_id,
            user_id=user_id,
        )
        participants_count = await self.uow.participants.count_participants(
            only_votable=True, nomination_id=nomination_id
        )
        return Page(
            items=participants,
            number=page,
            total=math.ceil(participants_count / participants_per_page),
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
            return vote.to_dto()

    async def cancel_vote(self, vote_id: int) -> None:
        vote = await self.uow.votes.get_vote(vote_id)
        if not vote:
            raise VoteNotFound
        async with self.uow:
            await self.uow.session.delete(vote)
            await self.uow.commit()