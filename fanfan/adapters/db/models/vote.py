from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fanfan.adapters.db.models.base import Base
from fanfan.core.models.participant import ParticipantId
from fanfan.core.models.user import UserId
from fanfan.core.models.vote import Vote, VoteId

if TYPE_CHECKING:
    from fanfan.adapters.db.models.nomination import DBNomination
    from fanfan.adapters.db.models.participant import DBParticipant
    from fanfan.adapters.db.models.user import DBUser


class DBVote(Base):
    __tablename__ = "votes"

    id: Mapped[int] = mapped_column(primary_key=True)

    # User relation
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    user: Mapped[DBUser] = relationship()

    # Participant relation
    participant_id: Mapped[int] = mapped_column(
        ForeignKey("participants.id", ondelete="CASCADE"),
    )
    participant: Mapped[DBParticipant] = relationship()
    nomination: Mapped[DBNomination] = relationship(
        secondary="participants",
        viewonly=True,
    )

    # User can vote once for participant
    UniqueConstraint(user_id, participant_id)

    @classmethod
    def from_model(cls, model: Vote):
        return DBVote(
            id=model.id,
            user_id=model.user_id,
            participant_id=model.participant_id,
        )

    def to_model(self) -> Vote:
        return Vote(
            id=VoteId(self.id),
            user_id=UserId(self.user_id),
            participant_id=ParticipantId(self.participant_id),
        )
