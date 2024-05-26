from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, case, func, select
from sqlalchemy.orm import (
    Mapped,
    column_property,
    mapped_column,
    relationship,
)

from fanfan.application.dto.event import EventDTO, FullEventDTO, ScheduleEventDTO
from fanfan.infrastructure.db.models.base import Base
from fanfan.infrastructure.db.models.mixins.order import OrderMixin

if TYPE_CHECKING:
    from fanfan.infrastructure.db.models.nomination import Nomination
    from fanfan.infrastructure.db.models.participant import Participant
    from fanfan.infrastructure.db.models.subscription import Subscription


class Event(Base, OrderMixin):
    __tablename__ = "schedule"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(index=True)

    # Event status
    current: Mapped[Optional[bool]] = mapped_column(nullable=True, unique=True)
    skip: Mapped[bool] = mapped_column(server_default="False")

    # Participant relation
    participant_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("participants.id", ondelete="CASCADE"),
        nullable=True,
    )
    participant: Mapped[Optional[Participant]] = relationship(back_populates="event")
    nomination: Mapped[Optional[Nomination]] = relationship(
        secondary="participants",
        viewonly=True,
    )

    # User subscription relation
    user_subscription: Mapped[Optional[Subscription]] = relationship(
        lazy="noload",
        viewonly=True,
    )

    def to_dto(self) -> EventDTO:
        return EventDTO.model_validate(self)

    def to_schedule_dto(self) -> ScheduleEventDTO:
        return ScheduleEventDTO.model_validate(self)

    def to_full_dto(self) -> FullEventDTO:
        return FullEventDTO.model_validate(self)

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
    deferred=True,
    expire_on_flush=True,
)
