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

from fanfan.core.models.event import EventDTO, FullEventDTO, UserFullEventDTO
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
    current: Mapped[bool | None] = mapped_column(nullable=True, unique=True)
    skip: Mapped[bool] = mapped_column(server_default="False")

    # Participant relation
    participant_id: Mapped[int | None] = mapped_column(
        ForeignKey("participants.id", ondelete="CASCADE"),
        nullable=True,
    )
    participant: Mapped[Participant | None] = relationship(back_populates="event")
    nomination: Mapped[Nomination | None] = relationship(
        secondary="participants",
        viewonly=True,
    )

    # User subscription relation
    user_subscription: Mapped[Subscription | None] = relationship(
        viewonly=True,
    )

    @declared_attr
    @classmethod
    def queue(cls) -> Mapped[int]:
        queue_subquery = select(
            cls.id,
            func.row_number()
            .over(order_by=cls.order, partition_by=cls.skip)
            .label("queue"),
        ).subquery()
        return column_property(
            select(
                case(
                    (
                        cls.skip.isnot(True),
                        queue_subquery.c.queue,
                    ),
                    else_=None,
                )
            )
            .where(cls.id == queue_subquery.c.id)
            .scalar_subquery(),
            expire_on_flush=True,
        )

    def __str__(self) -> str:
        return self.title

    def to_dto(self) -> EventDTO:
        return EventDTO(
            id=self.id,
            title=self.title,
            current=self.current,
            skip=self.skip,
            queue=self.queue,
        )

    def to_full_dto(self) -> FullEventDTO:
        self.nomination: Nomination
        return FullEventDTO(
            id=self.id,
            title=self.title,
            current=self.current,
            skip=self.skip,
            queue=self.queue,
            nomination=self.nomination.to_dto() if self.nomination else None,
        )

    def to_user_full_dto(self) -> UserFullEventDTO:
        self.nomination: Nomination
        self.user_subscription: Subscription
        return UserFullEventDTO(
            id=self.id,
            title=self.title,
            current=self.current,
            skip=self.skip,
            queue=self.queue,
            nomination=self.nomination.to_dto() if self.nomination else None,
            subscription=self.user_subscription.to_dto()
            if self.user_subscription
            else None,
        )
