from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Identity, UniqueConstraint, func, select
from sqlalchemy.orm import Mapped, column_property, mapped_column, relationship

from fanfan.adapters.db.models.base import Base
from fanfan.adapters.db.models.vote import DBVote
from fanfan.core.models.nomination import NominationId
from fanfan.core.models.participant import (
    UNSET_SCOPED_ID,
    FullParticipant,
    Participant,
    ParticipantId,
    ParticipantScopedId,
)

if TYPE_CHECKING:
    from fanfan.adapters.db.models.event import DBEvent
    from fanfan.adapters.db.models.nomination import DBNomination


class DBParticipant(Base):
    __tablename__ = "participants"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(index=True)

    # Nomination relation
    nomination_id: Mapped[int | None] = mapped_column(
        ForeignKey("nominations.id", ondelete="SET NULL"),
    )
    nomination: Mapped[DBNomination | None] = relationship()

    # Nomination scoped id
    scoped_id: Mapped[int] = mapped_column(Identity(start=1))
    UniqueConstraint(nomination_id, scoped_id)

    # Relationships
    event: Mapped[DBEvent | None] = relationship(
        back_populates="participant", single_parent=True
    )
    user_vote: Mapped[DBVote | None] = relationship(lazy="noload", viewonly=True)
    votes_count = column_property(
        select(func.count(DBVote.id))
        .where(DBVote.participant_id == id)
        .correlate_except(DBVote)
        .scalar_subquery(),
        deferred=True,
    )

    def __str__(self) -> str:
        return self.title

    @classmethod
    def from_model(cls, model: Participant):
        data = {
            "id": model.id,
            "title": model.title,
            "nomination_id": model.nomination_id,
        }
        if model.scoped_id is not UNSET_SCOPED_ID:
            data.update(scoped_id=model.scoped_id)
        return DBParticipant(**data)

    def to_model(self) -> Participant:
        return Participant(
            id=ParticipantId(self.id),
            title=self.title,
            nomination_id=NominationId(self.nomination_id),
            scoped_id=ParticipantScopedId(self.scoped_id),
        )

    def to_full_model(self) -> FullParticipant:
        return FullParticipant(
            id=ParticipantId(self.id),
            title=self.title,
            nomination_id=NominationId(self.nomination_id),
            scoped_id=ParticipantScopedId(self.scoped_id),
            event=self.event.to_model() if self.event else None,
            nomination=self.nomination.to_model() if self.nomination else None,
            votes_count=self.votes_count,
            user_vote=self.user_vote.to_model() if self.user_vote else None,
        )
