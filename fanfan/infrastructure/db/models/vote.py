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
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    participant_id: Mapped[int] = mapped_column(
        ForeignKey("participants.id", ondelete="CASCADE")
    )

    UniqueConstraint(user_id, participant_id)

    user: Mapped[User] = relationship()
    participant: Mapped[Participant] = relationship()
    nomination: Mapped[Nomination] = relationship(
        secondary="participants", viewonly=True
    )

    def to_dto(self) -> VoteDTO:
        return VoteDTO(
            id=self.id,
            user_id=self.user_id,
            participant_id=self.participant_id,
        )
