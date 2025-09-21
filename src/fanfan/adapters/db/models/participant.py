from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint, func, select
from sqlalchemy.orm import Mapped, column_property, mapped_column, relationship

from fanfan.adapters.db.models.base import Base
from fanfan.adapters.db.models.vote import VoteORM
from fanfan.core.models.participant import (
    Participant,
)
from fanfan.core.vo.nomination import NominationId
from fanfan.core.vo.participant import ParticipantId, ParticipantVotingNumber

if TYPE_CHECKING:
    from fanfan.adapters.db.models.nomination import NominationORM
    from fanfan.adapters.db.models.schedule_event import ScheduleEventORM


class ParticipantORM(Base):
    __tablename__ = "participants"
    __table_args__ = (
        UniqueConstraint(
            "nomination_id", "voting_number", deferrable=True, initially="DEFERRED"
        ),
    )

    id: Mapped[ParticipantId] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(index=True)

    # Nomination relation
    nomination_id: Mapped[int] = mapped_column(
        ForeignKey("nominations.id", ondelete="CASCADE"),
    )
    nomination: Mapped[NominationORM] = relationship()

    # Nomination scoped id
    voting_number: Mapped[int | None] = mapped_column()

    # Relationships
    event: Mapped[ScheduleEventORM | None] = relationship(
        back_populates="participant", single_parent=True
    )
    votes_count = column_property(
        select(func.count(VoteORM.id))
        .where(VoteORM.participant_id == id)
        .correlate_except(VoteORM)
        .scalar_subquery(),
        deferred=True,
    )

    def __str__(self) -> str:
        return self.title

    @classmethod
    def from_model(cls, model: Participant):
        return ParticipantORM(
            id=model.id,
            title=model.title,
            nomination_id=model.nomination_id,
            voting_number=model.voting_number,
        )

    def to_model(self) -> Participant:
        return Participant(
            id=ParticipantId(self.id),
            title=self.title,
            nomination_id=NominationId(self.nomination_id),
            voting_number=ParticipantVotingNumber(self.voting_number),
        )
