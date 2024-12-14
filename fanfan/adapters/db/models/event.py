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
from fanfan.adapters.db.models.block import DBBlock
from fanfan.adapters.db.models.mixins.order import OrderMixin
from fanfan.core.models.event import Event, EventId, FullEvent

if TYPE_CHECKING:
    from fanfan.adapters.db.models.nomination import DBNomination
    from fanfan.adapters.db.models.participant import DBParticipant
    from fanfan.adapters.db.models.subscription import DBSubscription


class DBEvent(Base, OrderMixin):
    __tablename__ = "schedule"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(index=True)

    # Event status
    is_current: Mapped[bool | None] = mapped_column(unique=True)
    is_skipped: Mapped[bool] = mapped_column(server_default="False")

    # Participant relation
    participant_id: Mapped[int | None] = mapped_column(
        ForeignKey("participants.id", ondelete="SET NULL"),
    )
    participant: Mapped[DBParticipant | None] = relationship(
        back_populates="event", single_parent=True
    )
    nomination: Mapped[DBNomination | None] = relationship(
        secondary="participants",
        viewonly=True,
    )

    # User subscription relation
    user_subscription: Mapped[DBSubscription | None] = relationship(
        viewonly=True,
        lazy="noload",
    )

    @declared_attr
    @classmethod
    def block(cls) -> Mapped[DBBlock | None]:
        subquery = select(
            cls.id,
            select(DBBlock.id)
            .order_by(DBBlock.start_order.desc())
            .where(cls.order >= DBBlock.start_order)
            .limit(1)
            .label("block_id"),
        ).subquery()
        return relationship(
            DBBlock,
            primaryjoin=(cls.id == subquery.c.id),
            secondaryjoin=(DBBlock.id == subquery.c.block_id),
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

    def __str__(self) -> str:
        return self.title

    @classmethod
    def from_model(cls, model: Event):
        return DBEvent(
            id=model.id,
            title=model.title,
            is_current=model.is_current,
            is_skipped=model.is_skipped,
            order=model.order,
        )

    def to_model(self) -> Event:
        return Event(
            id=EventId(self.id),
            title=self.title,
            is_current=self.is_current,
            is_skipped=self.is_skipped,
            order=self.order,
        )

    def to_full_model(self) -> FullEvent:
        return FullEvent(
            id=EventId(self.id),
            title=self.title,
            is_current=self.is_current,
            is_skipped=self.is_skipped,
            order=self.order,
            queue=self.queue,
            nomination=self.nomination.to_model() if self.nomination else None,
            block=self.block.to_model() if self.block else None,
            user_subscription=self.user_subscription.to_model()
            if self.user_subscription
            else None,
        )
