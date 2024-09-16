from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager, joinedload, undefer

from fanfan.application.common.id_provider import IdProvider
from fanfan.core.exceptions.events import EventNotFound
from fanfan.core.models.event import UserFullEventDTO
from fanfan.infrastructure.db.models import Event, Subscription


class GetEventById:
    def __init__(self, session: AsyncSession, id_provider: IdProvider) -> None:
        self.session = session
        self.id_provider = id_provider

    async def __call__(
        self,
        event_id: int,
    ) -> UserFullEventDTO:
        query = (
            select(Event)
            .where(Event.id == event_id)
            .options(joinedload(Event.nomination), undefer(Event.queue))
        )

        if self.id_provider.get_current_user_id():
            query = query.options(contains_eager(Event.user_subscription)).outerjoin(
                Subscription,
                and_(
                    Subscription.event_id == Event.id,
                    Subscription.user_id == self.id_provider.get_current_user_id(),
                ),
            )

        event = await self.session.scalar(query)

        if event:
            return event.to_user_full_dto()
        raise EventNotFound
