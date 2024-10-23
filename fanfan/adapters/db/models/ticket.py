from __future__ import annotations

from typing import TYPE_CHECKING

from adaptix import Retort, name_mapping
from sqlalchemy import ForeignKey
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fanfan.adapters.db.models.base import Base
from fanfan.core.enums import UserRole
from fanfan.core.models.ticket import TicketId, TicketModel
from fanfan.core.models.user import UserId

if TYPE_CHECKING:
    from fanfan.adapters.db.models.user import User


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[str] = mapped_column(primary_key=True)
    role: Mapped[UserRole] = mapped_column(
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

    @classmethod
    def from_model(cls, model: TicketModel):
        retort = Retort(recipe=[name_mapping(omit_default=True)])
        return Ticket(**retort.dump(model))

    def to_model(self) -> TicketModel:
        return TicketModel(
            id=TicketId(self.id),
            role=UserRole(self.role),
            issued_by_id=UserId(self.issued_by_id),
        )
