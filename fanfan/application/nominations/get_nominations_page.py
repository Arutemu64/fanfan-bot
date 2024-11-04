from fanfan.adapters.db.repositories.nominations import NominationsRepository
from fanfan.application.common.id_provider import IdProvider
from fanfan.core.dto.page import Page, Pagination
from fanfan.core.models.nomination import FullNominationModel


class GetNominationsPage:
    def __init__(
        self, nominations_repo: NominationsRepository, id_provider: IdProvider
    ) -> None:
        self.nominations_repo = nominations_repo
        self.id_provider = id_provider

    async def __call__(
        self,
        only_votable: bool,
        pagination: Pagination | None = None,
    ) -> Page[FullNominationModel]:
        nominations = await self.nominations_repo.list_nominations(
            only_votable=only_votable,
            user_id=self.id_provider.get_current_user_id(),
            pagination=pagination,
        )
        total = await self.nominations_repo.count_nominations(only_votable=only_votable)

        return Page(
            items=nominations,
            total=total,
        )
