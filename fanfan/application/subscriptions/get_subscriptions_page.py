from fanfan.adapters.db.repositories.subscriptions import (
    SubscriptionsRepository,
)
from fanfan.application.common.id_provider import IdProvider
from fanfan.application.common.interactor import Interactor
from fanfan.core.dto.page import Page, Pagination
from fanfan.core.models.subscription import SubscriptionFull


class GetSubscriptionsPage(Interactor[Pagination, Page[SubscriptionFull]]):
    def __init__(
        self,
        subscriptions_repo: SubscriptionsRepository,
        id_provider: IdProvider,
    ) -> None:
        self.subscriptions_repo = subscriptions_repo
        self.id_provider = id_provider

    async def __call__(
        self,
        pagination: Pagination | None = None,
    ) -> Page[SubscriptionFull]:
        user_id = self.id_provider.get_current_user_id()
        subscriptions = await self.subscriptions_repo.list_subscriptions(
            user_id=user_id,
            pagination=pagination,
        )
        total = await self.subscriptions_repo.count_subscriptions(user_id)
        return Page(
            items=subscriptions,
            total=total,
        )
