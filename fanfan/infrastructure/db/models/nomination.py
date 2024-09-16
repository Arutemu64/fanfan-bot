from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import func, select
from sqlalchemy.orm import Mapped, column_property, mapped_column, relationship

from fanfan.core.models.nomination import NominationDTO, UserNominationDTO
from fanfan.infrastructure.db.models.base import Base
from fanfan.infrastructure.db.models.participant import Participant

if TYPE_CHECKING:
    from fanfan.infrastructure.db.models.vote import Vote


class Nomination(Base):
    __tablename__ = "nominations"

    id: Mapped[str] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(unique=True)
    votable: Mapped[bool] = mapped_column(server_default="False")

    # Relationships
    user_vote: Mapped[Vote | None] = relationship(
        secondary="participants",
        viewonly=True,
    )
    participants_count = column_property(
        select(func.count(Participant.id))
        .where(Participant.nomination_id == id)
        .correlate_except(Participant)
        .scalar_subquery(),
        deferred=True,
    )

    def __str__(self) -> str:
        return self.title

    def to_dto(self) -> NominationDTO:
        return NominationDTO(
            id=self.id,
            title=self.title,
            votable=self.votable,
        )

    def to_user_dto(self) -> UserNominationDTO:
        self.user_vote: Vote
        return UserNominationDTO(
            id=self.id,
            title=self.title,
            votable=self.votable,
            vote=self.user_vote.to_dto() if self.user_vote else None,
        )
