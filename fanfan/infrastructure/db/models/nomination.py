from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Mapped, column_property, mapped_column, relationship

from fanfan.application.dto.nomination import FullNominationDTO, NominationDTO
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
    user_vote: Mapped[Optional[Vote]] = relationship(
        lazy="noload",
        secondary="participants",
        viewonly=True,
    )
    participants_count = column_property(
        select(func.count())
        .where(Participant.nomination_id == id)
        .correlate_except(Participant)
        .scalar_subquery(),
        deferred=True,
    )

    def to_dto(self) -> NominationDTO:
        return NominationDTO.model_validate(self)

    def to_full_dto(self) -> FullNominationDTO:
        return FullNominationDTO.model_validate(self)

    def __str__(self):
        return self.title
