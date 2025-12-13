from dataclasses import dataclass

from fanfan.adapters.db.repositories.participants import ParticipantsRepository
from fanfan.core.dto.page import Page, Pagination
from fanfan.core.models.participant import Participant
from fanfan.core.vo.nomination import NominationId


@dataclass(frozen=True, slots=True)
class ListParticipantsDTO:
    pagination: Pagination | None = None

    # Query
    nomination_ids: list[NominationId] | None = None
    search_query: str | None = None


class ListParticipants:
    def __init__(self, participants_repo: ParticipantsRepository) -> None:
        self.participants_repo = participants_repo

    async def __call__(self, data: ListParticipantsDTO) -> Page[Participant]:
        participants = await self.participants_repo.list_participants(
            pagination=data.pagination,
            search_query=data.search_query,
            nomination_ids=data.nomination_ids,
        )
        total = await self.participants_repo.count_participants(
            search_query=data.search_query,
            nomination_ids=data.nomination_ids,
        )
        return Page(
            items=participants,
            total=total,
        )
