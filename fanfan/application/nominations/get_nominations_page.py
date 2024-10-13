from fanfan.application.common.id_provider import IdProvider
from fanfan.core.models.nomination import FullNominationModel
from fanfan.core.models.page import Page, Pagination
from fanfan.infrastructure.db.repositories.nominations import NominationsRepository


class GetNominationsPage:
    def __init__(
        self, nominations_repo: NominationsRepository, id_provider: IdProvider
    ) -> None:
        self.nominations_repo = nominations_repo
        self.id_provider = id_provider

    async def __call__(
        self,
        pagination: Pagination | None = None,
    ) -> Page[FullNominationModel]:
        nominations = await self.nominations_repo.list_nominations(
            user_id=self.id_provider.get_current_user_id(), pagination=pagination
        )
        total = await self.nominations_repo.count_nominations()

        return Page(
            items=nominations,
            total=total,
        )
