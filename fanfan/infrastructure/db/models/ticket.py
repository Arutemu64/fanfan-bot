from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fanfan.core.enums import UserRole
from fanfan.core.models.ticket import TicketDTO
from fanfan.infrastructure.db.models.base import Base

if TYPE_CHECKING:
    from fanfan.infrastructure.db.models.user import User


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[str] = mapped_column(primary_key=True)
    role: Mapped[int] = mapped_column(
        postgresql.ENUM(UserRole),
        server_default="VISITOR",
    )

    # Users relations
    used_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        unique=True,
    )
    used_by: Mapped[User | None] = relationship(
        foreign_keys=used_by_id,
        back_populates="ticket",
    )
    issued_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    issued_by: Mapped[User | None] = relationship(foreign_keys=issued_by_id)

    def __str__(self) -> str:
        return self.id

    def to_dto(self) -> TicketDTO:
        return TicketDTO(
            id=self.id,
            role=self.role,
            used_by_id=self.used_by_id,
            issued_by_id=self.issued_by_id,
        )
