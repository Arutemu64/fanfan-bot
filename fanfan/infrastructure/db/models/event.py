import typing

from sqlalchemy import ForeignKey, Sequence, UniqueConstraint, case, func, select
from sqlalchemy.orm import (
    Mapped,
    column_property,
    mapped_column,
    relationship,
)

from fanfan.application.dto.event import EventDTO, FullEventDTO
from fanfan.infrastructure.db.models.base import Base

if typing.TYPE_CHECKING:
    from fanfan.infrastructure.db.models.nomination import Nomination
    from fanfan.infrastructure.db.models.participant import Participant
    from fanfan.infrastructure.db.models.subscription import Subscription


class Event(Base):
    __tablename__ = "schedule"

    def __str__(self):
        return self.title

    position_sequence = Sequence("schedule_position_seq", start=1)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(nullable=True, index=True)
    position: Mapped[float] = mapped_column(
        unique=True, nullable=False, server_default=position_sequence.next_value()
    )
    UniqueConstraint(position, deferrable=True, initially="DEFERRED")
    real_position: Mapped[int] = 0  # Placeholder
    participant_id: Mapped[int] = mapped_column(
        ForeignKey("participants.id", ondelete="CASCADE"), nullable=True
    )

    current: Mapped[bool] = mapped_column(nullable=True, unique=True)
    skip: Mapped[bool] = mapped_column(nullable=True, server_default="False")

    participant: Mapped["Participant"] = relationship(back_populates="event")
    nomination: Mapped["Nomination"] = relationship(
        secondary="participants",
        viewonly=True,
    )

    user_subscription: Mapped["Subscription"] = relationship(
        lazy="noload", viewonly=True
    )

    def to_dto(self) -> EventDTO:
        return EventDTO.model_validate(self)

    def to_full_dto(self) -> FullEventDTO:
        return FullEventDTO.model_validate(self)


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
    .scalar_subquery()
)
