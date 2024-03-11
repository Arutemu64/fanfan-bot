from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, func, select
from sqlalchemy.orm import Mapped, column_property, mapped_column, relationship

from fanfan.application.dto.participant import ParticipantDTO, VotingParticipantDTO
from fanfan.infrastructure.db.models.base import Base
from fanfan.infrastructure.db.models.vote import Vote

if TYPE_CHECKING:
    from fanfan.infrastructure.db.models.event import Event
    from fanfan.infrastructure.db.models.nomination import Nomination


class Participant(Base):
    __tablename__ = "participants"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(unique=True, index=True)
    nomination_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("nominations.id", ondelete="SET NULL"), nullable=True
    )

    event: Mapped[Optional[Event]] = relationship(
        back_populates="participant"
    )
    nomination: Mapped[Optional[Nomination]] = relationship()

    user_vote: Mapped[Optional[Vote]] = relationship(lazy="raise", viewonly=True)

    votes_count = column_property(
        select(func.count())
        .where(Vote.participant_id == id)
        .correlate_except(Vote)
        .scalar_subquery(),
        deferred=True,
    )

    def to_dto(self) -> ParticipantDTO:
        return ParticipantDTO(
            id=self.id,
            title=self.title,
            nomination_id=self.nomination_id,
        )

    def to_voting_dto(self) -> VotingParticipantDTO:
        return VotingParticipantDTO(
            id=self.id,
            title=self.title,
            nomination_id=self.nomination_id,
            votes_count=self.votes_count,
            user_vote=self.user_vote.to_dto() if self.user_vote else None,
        )

    def __str__(self):
        return self.title
