from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, case, func, select
from sqlalchemy.orm import (
    Mapped,
    column_property,
    declared_attr,
    mapped_column,
    relationship,
)

from fanfan.adapters.db.models.base import Base
from fanfan.adapters.db.models.mixins.order import OrderMixin
from fanfan.adapters.db.models.schedule_block import ScheduleBlockORM
from fanfan.core.models.schedule_event import (
    ScheduleEvent,
)
from fanfan.core.vo.schedule_event import ScheduleEventId, ScheduleEventPublicId

if TYPE_CHECKING:
    from fanfan.adapters.db.models.nomination import NominationORM
    from fanfan.adapters.db.models.participant import ParticipantORM


class ScheduleEventORM(Base, OrderMixin):
    __tablename__ = "schedule"

    id: Mapped[ScheduleEventId] = mapped_column(primary_key=True)

    public_id: Mapped[ScheduleEventPublicId] = mapped_column(unique=True)
    title: Mapped[str] = mapped_column(index=True)
    duration: Mapped[int] = mapped_column(server_default="0")

    # Event status
    is_current: Mapped[bool | None] = mapped_column(unique=True)
    is_skipped: Mapped[bool] = mapped_column(server_default="False")

    # Participant relation
    participant_id: Mapped[int | None] = mapped_column(
        ForeignKey("participants.id", ondelete="SET NULL"),
    )
    participant: Mapped[ParticipantORM | None] = relationship(
        back_populates="event", single_parent=True
    )
    nomination: Mapped[NominationORM | None] = relationship(
        secondary="participants",
        viewonly=True,
    )

    @declared_attr
    @classmethod
    def block(cls) -> Mapped[ScheduleBlockORM | None]:
        subquery = select(
            cls.id,
            select(ScheduleBlockORM.id)
            .order_by(ScheduleBlockORM.start_order.desc())
            .where(cls.order >= ScheduleBlockORM.start_order)
            .limit(1)
            .label("block_id"),
        ).subquery()
        return relationship(
            ScheduleBlockORM,
            primaryjoin=(cls.id == subquery.c.id),
            secondaryjoin=(ScheduleBlockORM.id == subquery.c.block_id),
            secondary=subquery,
            uselist=False,
            viewonly=True,
        )

    @declared_attr
    @classmethod
    def queue(cls) -> Mapped[int | None]:
        queue_subquery = select(
            cls.id,
            func.row_number()
            .over(order_by=cls.order, partition_by=cls.is_skipped)
            .label("queue"),
        ).subquery()
        query = select(
            case(
                (
                    cls.is_skipped.isnot(True),
                    queue_subquery.c.queue,
                ),
                else_=None,
            )
        ).where(cls.id == queue_subquery.c.id)
        return column_property(
            query.scalar_subquery(),
            expire_on_flush=True,
            deferred=True,
        )

    @declared_attr
    @classmethod
    def time_until(cls) -> Mapped[int]:
        current_event_order = (
            select(cls.order).where(cls.is_current.is_(True)).limit(1).scalar_subquery()
        )

        return column_property(
            select(func.coalesce(func.sum(cls.duration), 0))
            .where(
                cls.order >= current_event_order,
                cls.is_skipped.is_(False),
            )
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
            participant_id=model.participant_id,
        )

    def to_model(self) -> ScheduleEvent:
        return ScheduleEvent(
            id=ScheduleEventId(self.id),
            public_id=self.public_id,
            title=self.title,
            duration=self.duration,
            is_current=self.is_current,
            is_skipped=self.is_skipped,
            order=self.order,
            participant_id=self.participant_id,
        )
