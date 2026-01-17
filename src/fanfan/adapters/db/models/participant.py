from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint, func, select
from sqlalchemy.orm import Mapped, column_property, mapped_column, relationship

from fanfan.adapters.db.models.base import Base
from fanfan.adapters.db.models.vote import VoteORM
from fanfan.core.models.participant import (
    Participant,
    ParticipantValue,
)
from fanfan.core.vo.nomination import NominationId
from fanfan.core.vo.participant import ParticipantId, ParticipantVotingNumber, ValueType

if TYPE_CHECKING:
    from fanfan.adapters.db.models.nomination import NominationORM


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
    votes_count = column_property(
        select(func.count(VoteORM.id))
        .where(VoteORM.participant_id == id)
        .correlate_except(VoteORM)
        .scalar_subquery(),
        deferred=True,
    )

    values: Mapped[list[ParticipantValueORM]] = relationship(
        back_populates="participant",
        cascade="all, delete-orphan",
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
            values=[ParticipantValueORM.from_model(value) for value in model.values],
        )

    def to_model(self) -> Participant:
        return Participant(
            id=ParticipantId(self.id),
            title=self.title,
            nomination_id=NominationId(self.nomination_id),
            voting_number=ParticipantVotingNumber(self.voting_number),
            values=[value.to_model() for value in self.values],
        )


class ParticipantValueORM(Base):
    __tablename__ = "participant_values"

    id: Mapped[int] = mapped_column(primary_key=True)
    participant_id: Mapped[ParticipantId] = mapped_column(ForeignKey("participants.id"))
    title: Mapped[str] = mapped_column()
    type: Mapped[ValueType] = mapped_column()
    value: Mapped[str | None] = mapped_column()

    participant: Mapped[ParticipantORM] = relationship(back_populates="values")

    @classmethod
    def from_model(cls, model: ParticipantValue):
        return ParticipantValueORM(
            title=model.title,
            type=model.type,
            value=model.value,
        )

    def to_model(self) -> ParticipantValue:
        return ParticipantValue(
            title=self.title,
            type=self.type,
            value=self.value,
        )
