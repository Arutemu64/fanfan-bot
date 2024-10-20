from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fanfan.adapters.db.models.base import Base
from fanfan.core.models.participant import ParticipantId
from fanfan.core.models.user import UserId
from fanfan.core.models.vote import VoteId, VoteModel

if TYPE_CHECKING:
    from fanfan.adapters.db.models.nomination import Nomination
    from fanfan.adapters.db.models.participant import Participant
    from fanfan.adapters.db.models.user import User


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

    def to_model(self) -> VoteModel:
        return VoteModel(
            id=VoteId(self.id),
            user_id=UserId(self.user_id),
            participant_id=ParticipantId(self.participant_id),
        )
