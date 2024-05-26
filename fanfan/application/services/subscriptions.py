import logging

from sqlalchemy.exc import IntegrityError

from fanfan.application.dto.common import Page
from fanfan.application.dto.subscription import (
    CreateSubscriptionDTO,
    FullSubscriptionDTO,
)
from fanfan.application.exceptions.event import EventNotFound
from fanfan.application.exceptions.subscriptions import (
    SubscriptionAlreadyExist,
    SubscriptionNotFound,
)
from fanfan.application.exceptions.users import UserNotFound
from fanfan.application.services.base import BaseService

logger = logging.getLogger(__name__)


class SubscriptionsService(BaseService):
    async def create_subscription(
        self,
        dto: CreateSubscriptionDTO,
    ) -> FullSubscriptionDTO:
        """Create subscription for user"""
        async with self.uow:
            try:
                subscription = await self.uow.subscriptions.add_subscription(dto)
                await self.uow.commit()
                logger.info(
                    f"New subscription id={subscription.id} "
                    f"was created by user id={subscription.user_id}"
                )
                return await self.uow.subscriptions.get_subscription(subscription.id)
            except IntegrityError:
                await self.uow.rollback()
                subscription = await self.uow.subscriptions.get_subscription_by_event(
                    user_id=dto.user_id,
                    event_id=dto.event_id,
                )
                if subscription:
                    raise SubscriptionAlreadyExist
                event = await self.uow.events.get_event(dto.event_id)
                if event is None:
                    raise EventNotFound(event_id=dto.event_id)
                user = await self.uow.users.get_user_by_id(dto.user_id)
                if user is None:
                    raise UserNotFound

    async def get_subscription_by_event(
        self,
        user_id: int,
        event_id: int,
    ) -> FullSubscriptionDTO:
        """Get user_subscription for user"""
        if subscription := await self.uow.subscriptions.get_subscription_by_event(
            user_id=user_id,
            event_id=event_id,
        ):
            return subscription
        raise SubscriptionNotFound

    async def get_subscriptions_page(
        self,
        page_number: int,
        subscriptions_per_page: int,
        user_id: int,
    ) -> Page[FullSubscriptionDTO]:
        """Get page of subscriptions"""
        return await self.uow.subscriptions.paginate_subscriptions(
            page_number=page_number,
            subscriptions_per_page=subscriptions_per_page,
            user_id=user_id,
        )

    async def delete_subscription(self, subscription_id: int) -> None:
        """Delete user subscription by event id"""
        async with self.uow:
            await self.uow.subscriptions.delete_subscription(subscription_id)
            await self.uow.commit()
