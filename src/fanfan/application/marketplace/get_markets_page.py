from fanfan.adapters.db.repositories.markets import MarketsRepository
from fanfan.application.common.id_provider import IdProvider
from fanfan.core.dto.page import Page, Pagination
from fanfan.core.models.market import Market


class GetMarketsPage:
    def __init__(self, markets_repo: MarketsRepository, id_provider: IdProvider):
        self.markets_repo = markets_repo
        self.id_provider = id_provider

    async def __call__(self, pagination: Pagination) -> Page[Market]:
        user = await self.id_provider.get_current_user()
        markets = await self.markets_repo.read_markets(
            pagination=pagination,
            user_id=user.id,
        )
        total = await self.markets_repo.count_markets(user_id=user.id)
        return Page(items=markets, total=total)
