from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Sequence, UniqueConstraint, func, select
from sqlalchemy.orm import Mapped, column_property, mapped_column, relationship

from fanfan.application.dto.participant import (
    FullParticipantDTO,
    ParticipantDTO,
    VotingParticipantDTO,
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
    nomination_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("nominations.id", ondelete="SET NULL"),
        nullable=True,
    )
    nomination: Mapped[Optional[Nomination]] = relationship()
    order_sequence = Sequence("participants_scoped_id_seq", start=1)
    scoped_id: Mapped[int] = mapped_column(
        server_default=order_sequence.next_value()
    )  # ID inside nomination
    UniqueConstraint(nomination_id, scoped_id)

    # Relationships
    event: Mapped[Optional[Event]] = relationship(back_populates="participant")
    user_vote: Mapped[Optional[Vote]] = relationship(lazy="noload", viewonly=True)
    votes_count = column_property(
        select(func.count())
        .where(Vote.participant_id == id)
        .correlate_except(Vote)
        .scalar_subquery(),
        deferred=True,
    )

    def to_dto(self) -> ParticipantDTO:
        return ParticipantDTO.model_validate(self)

    def to_full_dto(self) -> FullParticipantDTO:
        return FullParticipantDTO.model_validate(self)

    def to_voting_dto(self) -> VotingParticipantDTO:
        return VotingParticipantDTO.model_validate(self)

    def __str__(self):
        return self.title
