from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Mapped, column_property, mapped_column

from fanfan.adapters.db.models.base import Base
from fanfan.adapters.db.models.participant import ParticipantORM
from fanfan.core.models.nomination import (
    Nomination,
    NominationId,
)


class NominationORM(Base):
    __tablename__ = "nominations"

    id: Mapped[NominationId] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(unique=True)
    title: Mapped[str] = mapped_column(unique=True)
    is_votable: Mapped[bool] = mapped_column(server_default="False")

    participants_count = column_property(
        select(func.count(ParticipantORM.id))
        .where(ParticipantORM.nomination_id == id)
        .correlate_except(ParticipantORM)
        .scalar_subquery(),
        deferred=True,
    )

    def __str__(self) -> str:
        return self.title

    @classmethod
    def from_model(cls, model: Nomination):
        return NominationORM(
            id=model.id,
            code=model.code,
            title=model.title,
            is_votable=model.is_votable,
        )

    def to_model(self) -> Nomination:
        return Nomination(
            id=NominationId(self.id),
            code=self.code,
            title=self.title,
            is_votable=self.is_votable,
        )
