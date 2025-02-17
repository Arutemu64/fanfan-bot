from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import func, select
from sqlalchemy.orm import Mapped, column_property, mapped_column, relationship

from fanfan.adapters.db.models.base import Base
from fanfan.adapters.db.models.participant import DBParticipant
from fanfan.core.models.nomination import (
    UNSET_IS_VOTABLE,
    FullNomination,
    Nomination,
    NominationId,
)

if TYPE_CHECKING:
    from fanfan.adapters.db.models.vote import DBVote


class DBNomination(Base):
    __tablename__ = "nominations"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(unique=True)
    title: Mapped[str] = mapped_column(unique=True)
    is_votable: Mapped[bool] = mapped_column(server_default="False")

    # Relationships
    user_vote: Mapped[DBVote | None] = relationship(
        secondary="participants",
        viewonly=True,
        lazy="noload",
    )
    participants_count = column_property(
        select(func.count(DBParticipant.id))
        .where(DBParticipant.nomination_id == id)
        .correlate_except(DBParticipant)
        .scalar_subquery(),
        deferred=True,
    )

    def __str__(self) -> str:
        return self.title

    @classmethod
    def from_model(cls, model: Nomination):
        data = {"id": model.id, "code": model.code, "title": model.title}
        if model.is_votable is not UNSET_IS_VOTABLE:
            data.update(is_votable=model.is_votable)
        return DBNomination(**data)

    def to_model(self) -> Nomination:
        return Nomination(
            id=NominationId(self.id),
            code=self.code,
            title=self.title,
            is_votable=self.is_votable,
        )

    def to_full_model(self) -> FullNomination:
        return FullNomination(
            id=NominationId(self.id),
            code=self.code,
            title=self.title,
            is_votable=self.is_votable,
            user_vote=self.user_vote.to_model() if self.user_vote else None,
        )
