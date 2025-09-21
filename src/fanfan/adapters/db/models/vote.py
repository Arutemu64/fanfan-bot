from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fanfan.adapters.db.models.base import Base
from fanfan.core.models.vote import Vote
from fanfan.core.vo.participant import ParticipantId
from fanfan.core.vo.user import UserId
from fanfan.core.vo.vote import VoteId

if TYPE_CHECKING:
    from fanfan.adapters.db.models.nomination import NominationORM
    from fanfan.adapters.db.models.participant import ParticipantORM
    from fanfan.adapters.db.models.user import UserORM


class VoteORM(Base):
    __tablename__ = "votes"
    __table_args__ = (UniqueConstraint("user_id", "participant_id"),)

    id: Mapped[VoteId] = mapped_column(primary_key=True)

    # User relation
    user_id: Mapped[UserId] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    user: Mapped[UserORM] = relationship()

    # Participant relation
    participant_id: Mapped[ParticipantId] = mapped_column(
        ForeignKey("participants.id", ondelete="CASCADE"),
    )
    participant: Mapped[ParticipantORM] = relationship()
    nomination: Mapped[NominationORM] = relationship(
        secondary="participants",
        viewonly=True,
    )

    @classmethod
    def from_model(cls, model: Vote):
        return VoteORM(
            id=model.id,
            user_id=model.user_id,
            participant_id=model.participant_id,
        )

    def to_model(self) -> Vote:
        return Vote(
            id=self.id,
            user_id=self.user_id,
            participant_id=self.participant_id,
        )
