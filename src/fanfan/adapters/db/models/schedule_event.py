from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import (
    Mapped,
    column_property,
    declared_attr,
    mapped_column,
)

from fanfan.adapters.db.models.base import Base
from fanfan.adapters.db.models.mixins.order import OrderMixin
from fanfan.core.models.schedule_event import (
    ScheduleEvent,
)
from fanfan.core.vo.schedule_event import ScheduleEventId, ScheduleEventPublicId


class ScheduleEventORM(Base, OrderMixin):
    __tablename__ = "schedule"

    id: Mapped[ScheduleEventId] = mapped_column(primary_key=True)
    public_id: Mapped[ScheduleEventPublicId] = mapped_column(unique=True)
    title: Mapped[str] = mapped_column(index=True)
    duration: Mapped[int] = mapped_column(server_default="0")
    is_current: Mapped[bool | None] = mapped_column(unique=True)
    is_skipped: Mapped[bool] = mapped_column(server_default="False")
    nomination_title: Mapped[str | None] = mapped_column()
    block_title: Mapped[str | None] = mapped_column()

    @declared_attr
    @classmethod
    def queue(cls) -> Mapped[int | None]:
        queue_subquery = (
            select(
                cls.id,
                func.row_number().over(order_by=cls.order).label("queue"),
            )
            .where(cls.is_skipped.isnot(True))
            .subquery()
        )
        stmt = select(queue_subquery.c.queue).where(cls.id == queue_subquery.c.id)
        return column_property(
            stmt.scalar_subquery(),
            expire_on_flush=True,
            deferred=True,
        )

    @declared_attr
    @classmethod
    def cumulative_duration(cls) -> Mapped[int | None]:
        stmt = (
            select(
                cls.id,
                func.coalesce(
                    func.sum(cls.duration).over(order_by=cls.order, range_=(None, -1)),
                    0,
                ).label("cumulative_duration"),
            )
            .where(cls.is_skipped.isnot(True))
            .subquery()
        )

        return column_property(
            select(stmt.c.cumulative_duration)
            .where(cls.id == stmt.c.id)
            .scalar_subquery(),
            expire_on_flush=True,
            deferred=True,
        )

    def __str__(self) -> str:
        return self.title

    @classmethod
    def from_model(cls, model: ScheduleEvent):
        return ScheduleEventORM(
            id=model.id,
            public_id=model.public_id,
            title=model.title,
            duration=model.duration,
            is_current=model.is_current,
            is_skipped=model.is_skipped,
            order=model.order,
            nomination_title=model.nomination_title,
            block_title=model.block_title,
        )

    def to_model(self) -> ScheduleEvent:
        return ScheduleEvent(
            id=self.id,
            public_id=self.public_id,
            title=self.title,
            duration=self.duration,
            is_current=self.is_current,
            is_skipped=self.is_skipped,
            order=self.order,
            nomination_title=self.nomination_title,
            block_title=self.block_title,
        )
