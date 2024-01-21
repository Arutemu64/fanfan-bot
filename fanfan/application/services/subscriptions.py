import math

from sqlalchemy.exc import IntegrityError

from fanfan.application.dto.common import Page
from fanfan.application.dto.subscription import CreateSubscriptionDTO, SubscriptionDTO
from fanfan.application.exceptions.event import EventNotFound
from fanfan.application.exceptions.subscriptions import (
    SubscriptionAlreadyExist,
    SubscriptionNotFound,
)
from fanfan.application.services.base import BaseService
from fanfan.infrastructure.db.models import Subscription


class SubscriptionsService(BaseService):
    async def create_subscription(
        self,
        dto: CreateSubscriptionDTO,
    ) -> SubscriptionDTO:
        """
        Create subscription for user
        """
        async with self.uow:
            try:
                subscription = Subscription(
                    user_id=dto.user_id,
                    event_id=dto.event_id,
                    counter=dto.counter,
                )
                self.uow.session.add(subscription)
                await self.uow.session.commit()
                await self.uow.session.refresh(subscription, ["event"])
                return subscription.to_dto()
            except IntegrityError:
                await self.uow.rollback()
                if not await self.uow.events.get_event(dto.event_id):
                    raise EventNotFound
                raise SubscriptionAlreadyExist
            pass

    async def get_subscription_by_event(
        self, user_id: int, event_id: int
    ) -> SubscriptionDTO:
        """
        Get user_subscription for user
        """
        if subscription := await self.uow.subscriptions.get_subscription_by_event(
            user_id, event_id
        ):
            return subscription.to_dto()
        raise SubscriptionNotFound

    async def get_subscriptions_page(
        self, page: int, subscriptions_per_page: int, user_id: int
    ) -> Page[SubscriptionDTO]:
        """
        Get page of subscriptions
        """
        subscriptions = await self.uow.subscriptions.paginate_subscriptions(
            page=page,
            subscriptions_per_page=subscriptions_per_page,
            user_id=user_id,
        )
        subscriptions_count = await self.uow.subscriptions.count_subscriptions(
            user_id=user_id
        )
        total = math.ceil(subscriptions_count / subscriptions_per_page)
        return Page(
            items=[s.to_dto() for s in subscriptions],
            number=page,
            total=total if total > 0 else 1,
        )

    async def update_subscription_counter(
        self, subscription_id: int, counter: int
    ) -> SubscriptionDTO:
        async with self.uow:
            subscription = await self.uow.subscriptions.get_subscription(
                subscription_id
            )
            if not subscription:
                raise SubscriptionNotFound
            subscription.counter = counter
            await self.uow.commit()
            return subscription.to_dto()

    async def delete_subscription(self, subscription_id: int) -> None:
        async with self.uow:
            subscription = await self.uow.subscriptions.get_subscription(
                subscription_id
            )
            if not subscription:
                raise SubscriptionNotFound
            await self.uow.session.delete(subscription)
            await self.uow.commit()

    async def delete_subscription_by_event(self, user_id: int, event_id: int) -> None:
        """
        Delete user_subscription
        """
        subscription = await self.uow.subscriptions.get_subscription_by_event(
            user_id, event_id
        )
        if not subscription:
            raise SubscriptionNotFound
        async with self.uow:
            await self.uow.session.delete(subscription)
            await self.uow.commit()
