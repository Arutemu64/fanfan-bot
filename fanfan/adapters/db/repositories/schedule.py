import math

from sqlalchemy import Select, and_, delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, undefer

from fanfan.adapters.db.models import (
    NominationORM,
    ScheduleChangeORM,
    ScheduleEventORM,
    SubscriptionORM,
)
from fanfan.core.dto.event import UserEventDTO
from fanfan.core.dto.page import Pagination
from fanfan.core.models.schedule_change import (
    ScheduleChange,
    ScheduleChangeFull,
    ScheduleChangeId,
)
from fanfan.core.models.schedule_event import (
    ScheduleEvent,
    ScheduleEventFull,
    ScheduleEventId,
)
from fanfan.core.models.user import UserId

EVENT_FULL_OPTIONS = (
    undefer(ScheduleEventORM.queue),
    joinedload(ScheduleEventORM.nomination),
    joinedload(ScheduleEventORM.block),
)


class ScheduleRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _to_user_dto(
        event: ScheduleEventORM, subscription: SubscriptionORM
    ) -> UserEventDTO:
        return UserEventDTO(
            id=ScheduleEventId(event.id),
            title=event.title,
            is_current=event.is_current,
            is_skipped=event.is_skipped,
            queue=event.queue,
            nomination=event.nomination.to_model() if event.nomination else None,
            block=event.block.to_model() if event.block else None,
            subscription=subscription.to_model() if subscription else None,
        )

    @staticmethod
    def _filter_events(
        stmt: Select,
        search_query: str | None,
    ) -> Select:
        if search_query:
            stmt = stmt.where(
                or_(
                    ScheduleEventORM.id == int(search_query)
                    if search_query.isnumeric()
                    else False,
                    ScheduleEventORM.title.ilike(f"%{search_query}%"),
                    ScheduleEventORM.nomination.has(
                        NominationORM.title.ilike(f"%{search_query}%")
                    ),
                ),
            )
        return stmt

    @staticmethod
    def _load_full(stmt: Select) -> Select:
        return stmt.options(*EVENT_FULL_OPTIONS)

    async def add_schedule_change(
        self, schedule_change: ScheduleChange
    ) -> ScheduleChange:
        schedule_change_orm = ScheduleChangeORM.from_model(schedule_change)
        self.session.add(schedule_change_orm)
        await self.session.flush([schedule_change_orm])
        return schedule_change_orm.to_model()

    async def save_schedule_change(
        self, schedule_change: ScheduleChange
    ) -> ScheduleChange:
        schedule_change_orm = ScheduleChangeORM.from_model(schedule_change)
        await self.session.merge(schedule_change_orm)
        await self.session.flush([schedule_change_orm])
        return schedule_change_orm.to_model()

    async def get_schedule_change(
        self, schedule_change_id: ScheduleChangeId
    ) -> ScheduleChangeFull | None:
        stmt = (
            select(ScheduleChangeORM)
            .where(ScheduleChangeORM.id == schedule_change_id)
            .options(
                joinedload(ScheduleChangeORM.user),
                joinedload(ScheduleChangeORM.changed_event).options(
                    *EVENT_FULL_OPTIONS
                ),
                joinedload(ScheduleChangeORM.argument_event).options(
                    *EVENT_FULL_OPTIONS
                ),
            )
        )
        schedule_change_orm = await self.session.scalar(stmt)
        return schedule_change_orm.to_full_model() if schedule_change_orm else None

    async def delete_schedule_change(self, schedule_change: ScheduleChange) -> None:
        await self.session.execute(
            delete(ScheduleChangeORM).where(ScheduleChangeORM.id == schedule_change.id)
        )

    async def get_event_by_id(
        self, event_id: ScheduleEventId
    ) -> ScheduleEventFull | None:
        stmt = select(ScheduleEventORM).where(ScheduleEventORM.id == event_id)
        stmt = self._load_full(stmt)
        event_orm = await self.session.scalar(stmt)
        return event_orm.to_full_model() if event_orm else None

    async def read_event_for_user(
        self, event_id: ScheduleEventId, user_id: UserId
    ) -> UserEventDTO | None:
        stmt = (
            select(ScheduleEventORM, SubscriptionORM)
            .where(ScheduleEventORM.id == event_id)
            .options(*EVENT_FULL_OPTIONS)
            .outerjoin(
                SubscriptionORM,
                and_(
                    SubscriptionORM.event_id == ScheduleEventORM.id,
                    SubscriptionORM.user_id == user_id,
                ),
            )
        )
        result = (await self.session.execute(stmt)).first()
        event_orm, subscription_orm = result
        return (
            self._to_user_dto(event=event_orm, subscription=subscription_orm)
            if result
            else None
        )

    async def get_event_by_queue(self, queue: int) -> ScheduleEvent | None:
        stmt = select(ScheduleEventORM).where(ScheduleEventORM.queue == queue).limit(1)
        event_orm = await self.session.scalar(stmt)
        return event_orm.to_model() if event_orm else None

    async def get_current_event(self) -> ScheduleEventFull | None:
        stmt = select(ScheduleEventORM).where(ScheduleEventORM.is_current.is_(True))
        stmt = self._load_full(stmt)
        event_orm = await self.session.scalar(stmt)
        return event_orm.to_full_model() if event_orm else None

    async def get_next_event(self) -> ScheduleEventFull | None:
        current_event_order = (
            select(ScheduleEventORM.order)
            .where(ScheduleEventORM.is_current.is_(True))
            .scalar_subquery()
        )
        stmt = (
            select(ScheduleEventORM)
            .order_by(ScheduleEventORM.order)
            .where(
                and_(
                    ScheduleEventORM.order > current_event_order,
                    ScheduleEventORM.is_skipped.is_not(True),
                )
            )
            .limit(1)
        )
        stmt = self._load_full(stmt)
        event_orm = await self.session.scalar(stmt)
        return event_orm.to_full_model() if event_orm else None

    async def get_next_by_order(self, order: float) -> ScheduleEvent | None:
        stmt = (
            select(ScheduleEventORM)
            .order_by(ScheduleEventORM.order)
            .where(ScheduleEventORM.order > order)
            .limit(1)
        )
        event_orm = await self.session.scalar(stmt)
        return event_orm.to_model() if event_orm else None

    async def get_previous_by_order(self, order: float) -> ScheduleEvent | None:
        stmt = (
            select(ScheduleEventORM)
            .order_by(ScheduleEventORM.order)
            .where(ScheduleEventORM.order < order)
            .limit(1)
        )
        event_orm = await self.session.scalar(stmt)
        return event_orm.to_model() if event_orm else None

    async def get_page_number_by_event(
        self, event_id: ScheduleEventId, events_per_page: int
    ) -> int | None:
        order_stmt = (
            select(ScheduleEventORM.order)
            .where(ScheduleEventORM.id == event_id)
            .scalar_subquery()
        )
        position_stmt = select(func.count(ScheduleEventORM.id)).where(
            ScheduleEventORM.order <= order_stmt
        )
        event_position = await self.session.scalar(position_stmt)
        if event_position > 0:
            return math.floor((event_position - 1) / events_per_page)
        return None

    async def read_events_list_for_user(
        self,
        user_id: UserId,
        search_query: str | None = None,
        pagination: Pagination | None = None,
    ) -> list[UserEventDTO]:
        stmt = (
            select(ScheduleEventORM, SubscriptionORM)
            .order_by(ScheduleEventORM.order)
            .options(*EVENT_FULL_OPTIONS)
            .outerjoin(
                SubscriptionORM,
                and_(
                    SubscriptionORM.event_id == ScheduleEventORM.id,
                    SubscriptionORM.user_id == user_id,
                ),
            )
        )

        if pagination:
            stmt = stmt.limit(pagination.limit).offset(pagination.offset)
        if search_query:
            stmt = self._filter_events(stmt, search_query)

        results = (await self.session.execute(stmt)).all()

        return [
            self._to_user_dto(event=event_orm, subscription=subscription_orm)
            for event_orm, subscription_orm in results
        ]

    async def count_events(
        self,
        search_query: str | None = None,
    ) -> int:
        stmt = select(func.count(ScheduleEventORM.id))
        if search_query:
            stmt = self._filter_events(stmt, search_query)
        return await self.session.scalar(stmt)

    async def save_event(self, event: ScheduleEvent) -> ScheduleEvent:
        event_orm = await self.session.merge(ScheduleEventORM.from_model(event))
        await self.session.flush([event_orm])
        return event_orm.to_model()
