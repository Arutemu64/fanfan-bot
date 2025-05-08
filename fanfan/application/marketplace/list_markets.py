from fanfan.adapters.db.repositories.markets import MarketsRepository
from fanfan.application.common.id_provider import IdProvider
from fanfan.core.dto.page import Page, Pagination
from fanfan.core.models.market import Market


class ListMarkets:
    def __init__(self, markets_repo: MarketsRepository, id_provider: IdProvider):
        self.markets_repo = markets_repo
        self.id_provider = id_provider

    async def __call__(self, pagination: Pagination) -> Page[Market]:
        user_id = self.id_provider.get_current_user_id()
        markets = await self.markets_repo.read_markets(
            is_visible=True,
            pagination=pagination,
            user_id=self.id_provider.get_current_user_id(),
        )
        total = await self.markets_repo.count_markets(is_visible=True, user_id=user_id)
        return Page(items=markets, total=total)
