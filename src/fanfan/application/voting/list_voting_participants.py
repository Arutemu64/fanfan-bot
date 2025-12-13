from dataclasses import dataclass

from fanfan.adapters.db.repositories.participants import ParticipantsRepository
from fanfan.application.common.id_provider import IdProvider
from fanfan.core.dto.page import Page, Pagination
from fanfan.core.dto.participant import VotingParticipantUserDTO
from fanfan.core.vo.nomination import NominationId


@dataclass(frozen=True, slots=True)
class GetVotingParticipantsDTO:
    nomination_id: NominationId
    pagination: Pagination | None = None
    search_query: str | None = None


class ListVotingParticipants:
    def __init__(
        self, participants_repo: ParticipantsRepository, id_provider: IdProvider
    ) -> None:
        self.participants_repo = participants_repo
        self.id_provider = id_provider

    async def __call__(
        self,
        data: GetVotingParticipantsDTO,
    ) -> Page[VotingParticipantUserDTO]:
        user = await self.id_provider.get_current_user()
        participants = (
            await self.participants_repo.list_voting_nomination_participants_for_user(
                user_id=user.id,
                nomination_id=data.nomination_id,
                search_query=data.search_query,
                pagination=data.pagination,
            )
        )
        total = await self.participants_repo.count_participants(
            nomination_ids=[data.nomination_id], search_query=data.search_query
        )

        return Page(
            items=participants,
            total=total,
        )
