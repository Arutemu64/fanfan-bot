from fanfan.adapters.db.repositories.nominations import NominationsRepository
from fanfan.application.common.id_provider import IdProvider
from fanfan.core.dto.page import Page, Pagination
from fanfan.core.models.nomination import NominationFull


class GetNominationsPage:
    def __init__(
        self, nominations_repo: NominationsRepository, id_provider: IdProvider
    ) -> None:
        self.nominations_repo = nominations_repo
        self.id_provider = id_provider

    async def __call__(
        self,
        pagination: Pagination | None = None,
    ) -> Page[NominationFull]:
        nominations = (
            await self.nominations_repo.read_votable_nominations_list_for_user(
                user_id=self.id_provider.get_current_user_id(), pagination=pagination
            )
        )
        total = await self.nominations_repo.count_votable_nominations()

        return Page(
            items=nominations,
            total=total,
        )
