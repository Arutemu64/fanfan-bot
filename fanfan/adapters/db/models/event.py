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
from fanfan.adapters.db.models.block import Block
from fanfan.adapters.db.models.mixins.order import OrderMixin
from fanfan.core.models.event import EventId, EventModel, FullEventModel

if TYPE_CHECKING:
    from fanfan.adapters.db.models.nomination import Nomination
    from fanfan.adapters.db.models.participant import Participant
    from fanfan.adapters.db.models.subscription import Subscription


class Event(Base, OrderMixin):
    __tablename__ = "schedule"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(index=True)

    # Event status
    current: Mapped[bool | None] = mapped_column(nullable=True, unique=True)
    skip: Mapped[bool] = mapped_column(server_default="False")

    # Participant relation
    participant_id: Mapped[int | None] = mapped_column(
        ForeignKey("participants.id", ondelete="SET NULL"),
        nullable=True,
    )
    participant: Mapped[Participant | None] = relationship(
        back_populates="event", single_parent=True
    )
    nomination: Mapped[Nomination | None] = relationship(
        secondary="participants",
        viewonly=True,
    )

    # User subscription relation
    user_subscription: Mapped[Subscription | None] = relationship(
        viewonly=True,
        lazy="noload",
    )

    @declared_attr
    @classmethod
    def block(cls) -> Mapped[Block | None]:
        subquery = select(
            cls.id,
            select(Block.id)
            .where(cls.order >= Block.start_order)
            .order_by(Block.start_order.desc())
            .limit(1)
            .label("block_id"),
        ).subquery()
        return relationship(
            Block,
            primaryjoin=(cls.id == subquery.c.id),
            secondaryjoin=(Block.id == subquery.c.block_id),
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

    def to_model(self) -> EventModel:
        return EventModel(
            id=EventId(self.id),
            title=self.title,
            current=self.current,
            skip=self.skip,
            order=self.order,
            queue=self.queue,
        )

    def to_full_model(self) -> FullEventModel:
        self.nomination: Nomination
        self.block: Block
        self.user_subscription: Subscription
        return FullEventModel(
            id=EventId(self.id),
            title=self.title,
            current=self.current,
            skip=self.skip,
            order=self.order,
            queue=self.queue,
            nomination=self.nomination.to_model() if self.nomination else None,
            block=self.block.to_model() if self.block else None,
            user_subscription=self.user_subscription.to_model()
            if self.user_subscription
            else None,
        )
