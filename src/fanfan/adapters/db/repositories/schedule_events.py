import math

from sqlalchemy import Select, and_, delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, undefer

from fanfan.adapters.db.models import (
    NominationORM,
    ScheduleEventORM,
    SubscriptionORM,
)
from fanfan.core.dto.page import Pagination
from fanfan.core.dto.schedule import (
    ScheduleEventBlockDTO,
    ScheduleEventDTO,
    ScheduleEventNominationDTO,
    ScheduleEventSubscriptionDTO,
    ScheduleEventUserDTO,
)
from fanfan.core.models.schedule_event import (
    ScheduleEvent,
)
from fanfan.core.vo.participant import ParticipantId
from fanfan.core.vo.schedule_event import ScheduleEventId, ScheduleEventPublicId
from fanfan.core.vo.user import UserId


def _select_schedule_event_dto() -> Select:
    return select(ScheduleEventORM).options(
        undefer(ScheduleEventORM.queue),
        undefer(ScheduleEventORM.cumulative_duration),
        joinedload(ScheduleEventORM.nomination),
        joinedload(ScheduleEventORM.block),
    )


def _parse_schedule_event_dto(event_orm: ScheduleEventORM) -> ScheduleEventDTO:
    return ScheduleEventDTO(
        id=event_orm.id,
        public_id=event_orm.public_id,
        title=event_orm.title,
        is_current=event_orm.is_current,
        is_skipped=event_orm.is_skipped,
        order=event_orm.order,
        duration=event_orm.duration,
        queue=event_orm.queue,
        cumulative_duration=event_orm.cumulative_duration,
        nomination=ScheduleEventNominationDTO(
            id=event_orm.nomination.id, title=event_orm.nomination.title
        )
        if event_orm.nomination
        else None,
        block=ScheduleEventBlockDTO(id=event_orm.block.id, title=event_orm.block.title)
        if event_orm.block
        else None,
    )


def _select_schedule_event_user_dto(user_id: UserId | None) -> Select:
    return (
        select(ScheduleEventORM, SubscriptionORM)
        .outerjoin(
            SubscriptionORM,
            and_(
                SubscriptionORM.event_id == ScheduleEventORM.id,
                SubscriptionORM.user_id == user_id,
            ),
        )
        .options(
            undefer(ScheduleEventORM.queue),
            undefer(ScheduleEventORM.cumulative_duration),
            joinedload(ScheduleEventORM.nomination),
            joinedload(ScheduleEventORM.block),
        )
    )


def _parse_schedule_event_user_dto(
    event_orm: ScheduleEventORM, subscription_orm: SubscriptionORM | None
) -> ScheduleEventUserDTO:
    return ScheduleEventUserDTO(
        id=event_orm.id,
        public_id=event_orm.public_id,
        title=event_orm.title,
        is_current=event_orm.is_current,
        is_skipped=event_orm.is_skipped,
        order=event_orm.order,
        duration=event_orm.duration,
        queue=event_orm.queue,
        cumulative_duration=event_orm.cumulative_duration,
        nomination=ScheduleEventNominationDTO(
            id=event_orm.nomination.id, title=event_orm.nomination.title
        )
        if event_orm.nomination
        else None,
        block=ScheduleEventBlockDTO(id=event_orm.block.id, title=event_orm.block.title)
        if event_orm.block
        else None,
        subscription=ScheduleEventSubscriptionDTO(
            id=subscription_orm.id, counter=subscription_orm.counter
        )
        if subscription_orm
        else None,
    )


def _filter_schedule_events(
    stmt: Select,
    search_query: str | None,
) -> Select:
    filters = []
    if search_query:
        filters.append(ScheduleEventORM.title.ilike(f"%{search_query}%"))
        filters.append(
            ScheduleEventORM.nomination.has(
                NominationORM.title.ilike(f"%{search_query}%")
            )
        )
        if search_query.isnumeric():
            filters.append(ScheduleEventORM.id == int(search_query))

    return stmt.where(or_(*filters))


class ScheduleEventsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_event(self, event: ScheduleEvent) -> ScheduleEvent:
        event_orm = ScheduleEventORM.from_model(event)
        self.session.add(event_orm)
        await self.session.flush([event_orm])
        return event_orm.to_model()

    async def get_event_by_id(self, event_id: ScheduleEventId) -> ScheduleEvent | None:
        stmt = select(ScheduleEventORM).where(ScheduleEventORM.id == event_id)
        event_orm = await self.session.scalar(stmt)
        return event_orm.to_model() if event_orm else None

    async def get_event_by_participant_id(
        self, participant_id: ParticipantId
    ) -> ScheduleEvent | None:
        stmt = select(ScheduleEventORM).where(
            ScheduleEventORM.participant_id == participant_id
        )
        event_orm = await self.session.scalar(stmt)
        return event_orm.to_model() if event_orm else None

    async def get_current_event(self) -> ScheduleEvent | None:
        stmt = select(ScheduleEventORM).where(ScheduleEventORM.is_current.is_(True))
        event_orm = await self.session.scalar(stmt)
        return event_orm.to_model() if event_orm else None

    async def get_all_events(self) -> list[ScheduleEvent]:
        stmt = select(ScheduleEventORM)
        event_orm = await self.session.scalars(stmt)
        return [e.to_model() for e in event_orm]

    async def read_next_event(self) -> ScheduleEventDTO | None:
        current_event_order = (
            select(ScheduleEventORM.order)
            .where(ScheduleEventORM.is_current.is_(True))
            .scalar_subquery()
        )
        stmt = (
            _select_schedule_event_dto()
            .order_by(ScheduleEventORM.order)
            .where(
                and_(
                    ScheduleEventORM.order > current_event_order,
                    ScheduleEventORM.is_skipped.is_not(True),
                )
            )
            .limit(1)
        )
        event_orm = await self.session.scalar(stmt)
        return _parse_schedule_event_dto(event_orm) if event_orm else None

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

    async def save_event(self, event: ScheduleEvent) -> ScheduleEvent:
        event_orm = await self.session.merge(ScheduleEventORM.from_model(event))
        await self.session.flush([event_orm])
        return event_orm.to_model()

    async def delete_event(self, event: ScheduleEvent) -> None:
        await self.session.execute(
            delete(ScheduleEventORM).where(ScheduleEventORM.id == event.id)
        )

    async def read_event_by_id(
        self, event_id: ScheduleEventId
    ) -> ScheduleEventDTO | None:
        stmt = _select_schedule_event_dto().where(ScheduleEventORM.id == event_id)
        event_orm = await self.session.scalar(stmt)
        return _parse_schedule_event_dto(event_orm) if event_orm else None

    async def read_event_user_by_id(
        self, event_id: ScheduleEventId, user_id: UserId | None = None
    ) -> ScheduleEventUserDTO | None:
        stmt = _select_schedule_event_user_dto(user_id).where(
            ScheduleEventORM.id == event_id
        )
        result = (await self.session.execute(stmt)).first()
        if result:
            event_orm, subscription_orm = result
            return _parse_schedule_event_user_dto(
                event_orm=event_orm, subscription_orm=subscription_orm
            )
        return None

    async def read_event_by_public_id(
        self, event_public_id: ScheduleEventPublicId
    ) -> ScheduleEventDTO | None:
        stmt = _select_schedule_event_dto().where(
            ScheduleEventORM.public_id == event_public_id
        )
        event_orm = await self.session.scalar(stmt)
        return _parse_schedule_event_dto(event_orm) if event_orm else None

    async def read_event_by_queue(self, queue: int) -> ScheduleEventDTO | None:
        stmt = _select_schedule_event_dto().where(ScheduleEventORM.queue == queue)
        event_orm = await self.session.scalar(stmt)
        return _parse_schedule_event_dto(event_orm) if event_orm else None

    async def read_current_event(self) -> ScheduleEventDTO | None:
        stmt = _select_schedule_event_dto().where(ScheduleEventORM.is_current.is_(True))
        event_orm = await self.session.scalar(stmt)
        return _parse_schedule_event_dto(event_orm) if event_orm else None

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

    async def list_schedule_for_user(
        self,
        user_id: UserId,
        search_query: str | None = None,
        pagination: Pagination | None = None,
    ) -> list[ScheduleEventUserDTO]:
        stmt = _select_schedule_event_user_dto(user_id).order_by(ScheduleEventORM.order)

        if search_query:
            stmt = _filter_schedule_events(stmt, search_query)
        if pagination:
            stmt = stmt.limit(pagination.limit).offset(pagination.offset)

        results = (await self.session.execute(stmt)).all()

        return [
            _parse_schedule_event_user_dto(
                event_orm=event_orm, subscription_orm=subscription_orm
            )
            for event_orm, subscription_orm in results
        ]

    async def count_events(
        self,
        search_query: str | None = None,
    ) -> int:
        stmt = select(func.count(ScheduleEventORM.id))
        if search_query:
            stmt = _filter_schedule_events(stmt, search_query)
        return await self.session.scalar(stmt)
