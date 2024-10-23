from dataclasses import dataclass

from fanfan.adapters.db.repositories.participants import ParticipantsRepository
from fanfan.application.common.id_provider import IdProvider
from fanfan.application.common.interactor import Interactor
from fanfan.core.models.nomination import NominationId
from fanfan.core.models.page import Page, Pagination
from fanfan.core.models.participant import FullParticipantModel


@dataclass(frozen=True, slots=True)
class GetParticipantsPageDTO:
    nomination_id: NominationId
    only_votable: bool
    pagination: Pagination | None = None
    search_query: str | None = None


class GetParticipantsPage(
    Interactor[GetParticipantsPageDTO, Page[FullParticipantModel]]
):
    def __init__(
        self, participants_repo: ParticipantsRepository, id_provider: IdProvider
    ) -> None:
        self.participants_repo = participants_repo
        self.id_provider = id_provider

    async def __call__(
        self,
        data: GetParticipantsPageDTO,
    ) -> Page[FullParticipantModel]:
        user_id = self.id_provider.get_current_user_id()
        participants = await self.participants_repo.list_participants(
            nomination_id=data.nomination_id,
            search_query=data.search_query,
            user_id=user_id,
            pagination=data.pagination,
            only_votable=True,
        )
        total = await self.participants_repo.count_participants(
            nomination_id=data.nomination_id,
            search_query=data.search_query,
            only_votable=True,
        )

        return Page(
            items=participants,
            total=total,
        )
