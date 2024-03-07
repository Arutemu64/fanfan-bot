from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fanfan.application.dto.ticket import TicketDTO
from fanfan.common.enums import UserRole
from fanfan.infrastructure.db.models.base import Base

if TYPE_CHECKING:
    from fanfan.infrastructure.db.models.user import User


class Ticket(Base):
    __tablename__ = "tickets"

    def __str__(self):
        return self.id

    id: Mapped[str] = mapped_column(primary_key=True)
    role: Mapped[int] = mapped_column(
        postgresql.ENUM(UserRole), server_default="VISITOR"
    )
    used_by_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        unique=True,
    )
    issued_by_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    used_by: Mapped[Optional[User]] = relationship(
        foreign_keys=used_by_id, back_populates="ticket"
    )
    issued_by: Mapped[Optional[User]] = relationship(foreign_keys=issued_by_id)

    def to_dto(self) -> TicketDTO:
        return TicketDTO.model_validate(self)
