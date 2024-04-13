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
    position_sequence = Sequence("schedule_position_seq", start=1)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(index=True)
    position: Mapped[float] = mapped_column(
        unique=True,
        nullable=False,
        server_default=position_sequence.next_value(),
    )
    UniqueConstraint(position, deferrable=True, initially="DEFERRED")
    real_position = None  # Placeholder
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


rp_subquery = select(
    Event.id.label("event_id"),
    case(
        (
            Event.skip.isnot(True),
            func.row_number().over(order_by=Event.position, partition_by=Event.skip),
        ),
        else_=None,
    ).label("real_position"),
).subquery()

Event.real_position = column_property(
    select(rp_subquery.c.real_position)
    .where(Event.id == rp_subquery.c.event_id)
    .scalar_subquery(),
    expire_on_flush=True,
)
