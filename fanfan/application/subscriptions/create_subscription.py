from dataclasses import dataclass

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.core.exceptions.events import EventNotFound
from fanfan.core.exceptions.subscriptions import SubscriptionAlreadyExist
from fanfan.core.exceptions.users import UserNotFound
from fanfan.core.models.subscription import (
    FullSubscriptionDTO,
)
from fanfan.infrastructure.db.models import Event, Subscription, User


@dataclass
class CreateSubscriptionDTO:
    user_id: int
    event_id: int
    counter: int


class CreateSubscription:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self.session = session

    async def __call__(
        self,
        dto: CreateSubscriptionDTO,
    ) -> FullSubscriptionDTO:
        async with self.session:
            try:
                user = await self.session.get(User, dto.user_id)
                if user is None:
                    raise UserNotFound

                event = await self.session.get(Event, dto.event_id)
                if event is None:
                    raise EventNotFound

                subscription = Subscription(user=user, event=event, counter=dto.counter)
                self.session.add(subscription)
                await self.session.commit()
                return subscription.to_full_dto()
            except IntegrityError as e:
                await self.session.rollback()
                raise SubscriptionAlreadyExist from e
