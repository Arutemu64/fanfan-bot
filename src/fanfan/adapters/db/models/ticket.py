from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fanfan.adapters.db.models.base import Base
from fanfan.core.models.ticket import Ticket
from fanfan.core.vo.ticket import TicketId
from fanfan.core.vo.user import UserId, UserRole

if TYPE_CHECKING:
    from fanfan.adapters.db.models.user import UserORM


class TicketORM(Base):
    __tablename__ = "tickets"

    id: Mapped[TicketId] = mapped_column(primary_key=True)
    role: Mapped[UserRole] = mapped_column(postgresql.ENUM(UserRole))

    # Users relations
    used_by_id: Mapped[UserId | None] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
    )
    used_by: Mapped[UserORM | None] = relationship(
        foreign_keys=used_by_id,
        back_populates="ticket",
    )

    issued_by_id: Mapped[UserId | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
    )
    issued_by: Mapped[UserORM | None] = relationship(foreign_keys=issued_by_id)

    def __str__(self) -> str:
        return self.id

    @classmethod
    def from_model(cls, model: Ticket):
        return TicketORM(
            id=model.id,
            role=model.role,
            used_by_id=model.used_by_id,
            issued_by_id=model.issued_by_id,
        )

    def to_model(self) -> Ticket:
        return Ticket(
            id=self.id,
            role=self.role,
            used_by_id=self.used_by_id,
            issued_by_id=self.issued_by_id,
        )
