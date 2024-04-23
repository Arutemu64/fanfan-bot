from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Sequence, UniqueConstraint, case, func, select
from sqlalchemy.orm import (
    Mapped,
    column_property,
    mapped_column,
    relationship,
)

from fanfan.application.dto.event import EventDTO, ScheduleEventDTO
from fanfan.infrastructure.db.models.base import Base

if TYPE_CHECKING:
    from fanfan.infrastructure.db.models.nomination import Nomination
    from fanfan.infrastructure.db.models.participant import Participant
    from fanfan.infrastructure.db.models.subscription import Subscription


class Event(Base):
    __tablename__ = "schedule"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(index=True)
    order: Mapped[float] = mapped_column(
        unique=True,
        nullable=False,
        server_default=Sequence("schedule_order_seq", start=1).next_value(),
    )
    UniqueConstraint(order, deferrable=True, initially="DEFERRED")
    position = None  # Placeholder
    participant_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("participants.id", ondelete="CASCADE"),
        nullable=True,
    )

    current: Mapped[Optional[bool]] = mapped_column(nullable=True, unique=True)
    skip: Mapped[bool] = mapped_column(server_default="False")

    participant: Mapped[Optional[Participant]] = relationship(back_populates="event")
    nomination: Mapped[Optional[Nomination]] = relationship(
        secondary="participants",
        viewonly=True,
    )

    user_subscription: Mapped[Optional[Subscription]] = relationship(
        lazy="raise",
        viewonly=True,
    )

    def to_dto(self) -> EventDTO:
        return EventDTO.model_validate(self)

    def to_schedule_dto(self) -> ScheduleEventDTO:
        return ScheduleEventDTO.model_validate(self)

    def __str__(self):
        return self.title


position_subquery = select(
    Event.id.label("event_id"),
    case(
        (
            Event.skip.isnot(True),
            func.row_number().over(order_by=Event.order, partition_by=Event.skip),
        ),
        else_=None,
    ).label("position"),
).subquery()

Event.position = column_property(
    select(position_subquery.c.position)
    .where(Event.id == position_subquery.c.event_id)
    .scalar_subquery(),
    expire_on_flush=True,
)
