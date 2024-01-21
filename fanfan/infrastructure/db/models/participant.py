from sqlalchemy import ForeignKey, func, select
from sqlalchemy.orm import Mapped, column_property, mapped_column, relationship

from fanfan.infrastructure.db.models.base import Base
from fanfan.infrastructure.db.models.vote import Vote


class Participant(Base):
    __tablename__ = "participants"

    def __str__(self):
        return self.title

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(unique=True, index=True)
    nomination_id: Mapped[str] = mapped_column(
        ForeignKey("nominations.id", ondelete="SET NULL"), nullable=True
    )

    event: Mapped["Event"] = relationship(back_populates="participant")  # noqa: F821
    nomination: Mapped["Nomination"] = relationship()  # noqa: F821

    user_vote: Mapped["Vote"] = relationship(lazy="noload", viewonly=True)

    votes_count = column_property(
        select(func.count())
        .where(Vote.participant_id == id)
        .correlate_except(Vote)
        .scalar_subquery(),
    )
