from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fanfan.application.dto.vote import VoteDTO
from fanfan.infrastructure.db.models.base import Base

if TYPE_CHECKING:
    from fanfan.infrastructure.db.models.nomination import Nomination
    from fanfan.infrastructure.db.models.participant import Participant
    from fanfan.infrastructure.db.models.user import User


class Vote(Base):
    __tablename__ = "votes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Participant relation
    participant_id: Mapped[int] = mapped_column(
        ForeignKey("participants.id", ondelete="CASCADE"),
    )
    participant: Mapped[Participant] = relationship()
    nomination: Mapped[Nomination] = relationship(
        secondary="participants",
        viewonly=True,
    )

    # User relation
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    user: Mapped[User] = relationship()
    UniqueConstraint(user_id, participant_id)  # User can vote once for participant

    def to_dto(self) -> VoteDTO:
        return VoteDTO.model_validate(self)
