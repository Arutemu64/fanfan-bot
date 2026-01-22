from sqlalchemy import and_, delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, undefer

from fanfan.adapters.db.models import ScheduleEventORM, SubscriptionORM
from fanfan.core.dto.subscription import SubscriptionDTO, SubscriptionEventDTO
from fanfan.core.models.subscription import (
    Subscription,
)
from fanfan.core.vo.schedule_event import ScheduleEventId
from fanfan.core.vo.subscription import SubscriptionId
from fanfan.core.vo.user import UserId


def _select_subscription_dto():
    return (
        select(SubscriptionORM)
        .join(ScheduleEventORM)
        .options(
            joinedload(SubscriptionORM.event).options(
                undefer(ScheduleEventORM.queue),
                undefer(ScheduleEventORM.cumulative_duration),
            )
        )
    )


def _parse_subscription_dto(subscription_orm: SubscriptionORM) -> SubscriptionDTO:
    return SubscriptionDTO(
        id=subscription_orm.id,
        user_id=subscription_orm.user_id,
        counter=subscription_orm.counter,
        event=SubscriptionEventDTO(
            id=subscription_orm.event.id,
            public_id=subscription_orm.event.public_id,
            title=subscription_orm.event.title,
            order=subscription_orm.event.order,
            queue=subscription_orm.event.queue,
            cumulative_duration=subscription_orm.event.cumulative_duration,
            is_skipped=subscription_orm.event.is_skipped,
        ),
    )


class SubscriptionsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_subscription(self, subscription: Subscription) -> Subscription:
        subscription_orm = SubscriptionORM.from_model(subscription)
        self.session.add(subscription_orm)
        await self.session.flush([subscription_orm])
        return subscription_orm.to_model()

    async def get_subscription_by_id(
        self, subscription_id: SubscriptionId
    ) -> Subscription | None:
        stmt = select(SubscriptionORM).where(SubscriptionORM.id == subscription_id)
        subscription_orm = await self.session.scalar(stmt)
        return subscription_orm.to_model() if subscription_orm else None

    async def get_user_subscription_by_event(
        self, user_id: UserId, event_id: ScheduleEventId
    ) -> Subscription | None:
        stmt = select(SubscriptionORM).where(
            and_(
                SubscriptionORM.user_id == user_id,
                SubscriptionORM.event_id == event_id,
            )
        )
        subscription_orm = await self.session.scalar(stmt)
        return subscription_orm.to_model() if subscription_orm else None

    async def delete_subscription(self, subscription: Subscription) -> None:
        await self.session.execute(
            delete(SubscriptionORM).where(SubscriptionORM.id == subscription.id)
        )

    async def read_user_subscription(
        self, subscription_id: SubscriptionId
    ) -> SubscriptionDTO | None:
        stmt = _select_subscription_dto().where(SubscriptionORM.id == subscription_id)

        subscription_orm = await self.session.scalar(stmt)

        return _parse_subscription_dto(subscription_orm) if subscription_orm else None

    async def read_upcoming_subscriptions(
        self, current_event_queue: int
    ) -> list[SubscriptionDTO]:
        stmt = _select_subscription_dto().where(
            # Ignore skipped events
            ScheduleEventORM.is_skipped.isnot(True),
            # Counter clause
            SubscriptionORM.counter >= (ScheduleEventORM.queue - current_event_queue),
            # Ignore past events due to previous clause
            (ScheduleEventORM.queue - current_event_queue) >= 0,
        )

        results = await self.session.scalars(stmt)

        return [
            _parse_subscription_dto(subscription_orm) for subscription_orm in results
        ]
