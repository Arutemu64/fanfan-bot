from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Sequence, UniqueConstraint, func, select
from sqlalchemy.orm import Mapped, column_property, mapped_column, relationship

from fanfan.core.models.participant import (
    FullParticipantModel,
    ParticipantId,
    ParticipantModel,
    ParticipantScopedId,
)
from fanfan.infrastructure.db.models.base import Base
from fanfan.infrastructure.db.models.vote import Vote

if TYPE_CHECKING:
    from fanfan.infrastructure.db.models.event import Event
    from fanfan.infrastructure.db.models.nomination import Nomination


class Participant(Base):
    __tablename__ = "participants"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(unique=True, index=True)

    # Nomination relation
    nomination_id: Mapped[str | None] = mapped_column(
        ForeignKey("nominations.id", ondelete="SET NULL"),
        nullable=True,
    )
    nomination: Mapped[Nomination | None] = relationship()
    order_sequence = Sequence("participants_scoped_id_seq", start=1)
    scoped_id: Mapped[int] = mapped_column(
        server_default=order_sequence.next_value(),
    )  # ID inside nomination
    UniqueConstraint(nomination_id, scoped_id)

    # Relationships
    event: Mapped[Event | None] = relationship(back_populates="participant")
    user_vote: Mapped[Vote | None] = relationship(lazy="noload", viewonly=True)
    votes_count = column_property(
        select(func.count(Vote.id))
        .where(Vote.participant_id == id)
        .correlate_except(Vote)
        .scalar_subquery(),
        deferred=True,
    )

    def __str__(self) -> str:
        return self.title

    def to_model(self) -> ParticipantModel:
        return ParticipantModel(
            id=ParticipantId(self.id),
            title=self.title,
            nomination_id=self.nomination_id,
            scoped_id=ParticipantScopedId(self.scoped_id),
        )

    def to_full_model(self) -> FullParticipantModel:
        return FullParticipantModel(
            id=ParticipantId(self.id),
            title=self.title,
            nomination_id=self.nomination_id,
            scoped_id=ParticipantScopedId(self.scoped_id),
            event=self.event.to_model() if self.event else None,
            nomination=self.nomination.to_model() if self.nomination else None,
            votes_count=self.votes_count,
            user_vote=self.user_vote.to_model() if self.user_vote else None,
        )
