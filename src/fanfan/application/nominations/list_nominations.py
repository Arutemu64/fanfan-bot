from dataclasses import dataclass

from fanfan.adapters.db.repositories.nominations import NominationsRepository
from fanfan.core.dto.page import Page, Pagination
from fanfan.core.models.nomination import Nomination


@dataclass(slots=True, frozen=True)
class ListNominationsDTO:
    pagination: Pagination | None = None


class ListNominations:
    def __init__(self, nominations_repo: NominationsRepository) -> None:
        self.nominations_repo = nominations_repo

    async def __call__(self, data: ListNominationsDTO) -> Page[Nomination]:
        nominations = await self.nominations_repo.list_nominations(
            pagination=data.pagination,
        )
        total = await self.nominations_repo.count_nominations()

        return Page(
            items=nominations,
            total=total,
        )
