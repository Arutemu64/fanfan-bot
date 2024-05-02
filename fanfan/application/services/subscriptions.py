import logging

from sqlalchemy.exc import IntegrityError

from fanfan.application.dto.common import Page
from fanfan.application.dto.subscription import CreateSubscriptionDTO, SubscriptionDTO
from fanfan.application.exceptions.event import EventNotFound, SkippedEventNotAllowed
from fanfan.application.exceptions.subscriptions import (
    SubscriptionAlreadyExist,
    SubscriptionNotFound,
)
from fanfan.application.services.base import BaseService
from fanfan.infrastructure.db.models import Subscription

logger = logging.getLogger(__name__)


class SubscriptionsService(BaseService):
    async def create_subscription(
        self,
        dto: CreateSubscriptionDTO,
    ) -> SubscriptionDTO:
        """Create subscription for user"""
        async with self.uow:
            try:
                event = await self.uow.events.get_event(dto.event_id)
                if event is None:
                    raise EventNotFound(event_id=dto.event_id)
                if event.skip:
                    raise SkippedEventNotAllowed
                subscription = Subscription(
                    user_id=dto.user_id,
                    event=event,
                    counter=dto.counter,
                )
                self.uow.session.add(subscription)
                await self.uow.session.commit()
                logger.info(
                    f"New subscription id={subscription.id} "
                    f"was created by user id={dto.user_id}"
                )
                return subscription.to_dto()
            except IntegrityError:
                await self.uow.rollback()
                raise SubscriptionAlreadyExist

    async def get_subscription_by_event(
        self,
        user_id: int,
        event_id: int,
    ) -> SubscriptionDTO:
        """Get user_subscription for user"""
        if subscription := await self.uow.subscriptions.get_subscription_by_event(
            user_id,
            event_id,
        ):
            return subscription.to_dto()
        raise SubscriptionNotFound

    async def get_subscriptions_page(
        self,
        page_number: int,
        subscriptions_per_page: int,
        user_id: int,
    ) -> Page[SubscriptionDTO]:
        """Get page of subscriptions"""
        page = await self.uow.subscriptions.paginate_subscriptions(
            page_number=page_number,
            subscriptions_per_page=subscriptions_per_page,
            user_id=user_id,
        )
        return Page(
            items=[s.to_dto() for s in page.items],
            number=page.number,
            total_pages=page.total_pages,
        )

    async def delete_subscription_by_event(self, user_id: int, event_id: int) -> None:
        """Delete user subscription by event id"""
        subscription = await self.uow.subscriptions.get_subscription_by_event(
            user_id,
            event_id,
        )
        if not subscription:
            raise SubscriptionNotFound
        async with self.uow:
            await self.uow.session.delete(subscription)
            await self.uow.commit()
            logger.info(
                f"Subscription id={subscription.id} was deleted by user id={user_id}"
            )
