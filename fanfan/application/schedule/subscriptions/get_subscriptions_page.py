from fanfan.adapters.db.repositories.subscriptions import SubscriptionsRepository
from fanfan.application.common.id_provider import IdProvider
from fanfan.core.dto.page import Page, Pagination
from fanfan.core.dto.subscription import SubscriptionDTO


class GetSubscriptionsPage:
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
    ) -> Page[SubscriptionDTO]:
        user_id = self.id_provider.get_current_user_id()
        subscriptions = await self.subscriptions_repo.list_user_subscriptions(
            user_id=user_id, pagination=pagination
        )
        total = await self.subscriptions_repo.count_user_subscriptions(user_id)
        return Page(
            items=subscriptions,
            total=total,
        )
