from dataclasses import dataclass

from fanfan.adapters.db.repositories.nominations import NominationsRepository
from fanfan.application.common.id_provider import IdProvider
from fanfan.core.dto.nomination import NominationUserDTO
from fanfan.core.dto.page import Page, Pagination


@dataclass(slots=True, frozen=True)
class GetNominationsPageDTO:
    pagination: Pagination | None = None


class GetNominationsPage:
    def __init__(
        self, nominations_repo: NominationsRepository, id_provider: IdProvider
    ) -> None:
        self.nominations_repo = nominations_repo
        self.id_provider = id_provider

    async def __call__(self, data: GetNominationsPageDTO) -> Page[NominationUserDTO]:
        user = await self.id_provider.get_current_user()
        nominations = await self.nominations_repo.read_votable_nominations_for_user(
            user_id=user.id, pagination=data.pagination
        )
        total = await self.nominations_repo.count_votable_nominations()

        return Page(
            items=nominations,
            total=total,
        )
