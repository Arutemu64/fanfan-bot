from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Sequence, func, select
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
    order: Mapped[float] = mapped_column(
        unique=True,
        nullable=False,
        server_default=Sequence("participants_order_seq", start=1).next_value(),
    )

    title: Mapped[str] = mapped_column(unique=True, index=True)
    nomination_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("nominations.id", ondelete="SET NULL"),
        nullable=True,
    )

    event: Mapped[Optional[Event]] = relationship(back_populates="participant")
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
        return ParticipantDTO.model_validate(self)

    def to_voting_dto(self) -> VotingParticipantDTO:
        return VotingParticipantDTO.model_validate(self)

    def __str__(self):
        return self.title


nomination_position_subquery = select(
    Participant.id.label("participant_id"),
    func.row_number()
    .over(order_by=Participant.order, partition_by=Participant.nomination_id)
    .label("nomination_position"),
).subquery()

Participant.nomination_position = column_property(
    select(nomination_position_subquery.c.nomination_position)
    .where(Participant.id == nomination_position_subquery.c.participant_id)
    .scalar_subquery(),
    expire_on_flush=True,
)
