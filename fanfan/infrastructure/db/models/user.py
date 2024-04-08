from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy import BigInteger, func, select
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import (
    Mapped,
    WriteOnlyMapped,
    column_property,
    mapped_column,
    relationship,
)

from fanfan.application.dto.user import FullUserDTO, UserDTO
from fanfan.common.enums import UserRole
from fanfan.infrastructure.db.models.base import Base
from fanfan.infrastructure.db.models.received_achievement import ReceivedAchievement

if TYPE_CHECKING:
    from fanfan.infrastructure.db.models.achievement import Achievement
    from fanfan.infrastructure.db.models.ticket import Ticket


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    username: Mapped[Optional[str]] = mapped_column(
        index=True,
        unique=False,
        nullable=True,
    )
    role: Mapped[UserRole] = mapped_column(
        postgresql.ENUM(UserRole),
        default=UserRole.VISITOR,
        server_default="VISITOR",
    )

    items_per_page: Mapped[int] = mapped_column(server_default="5")
    receive_all_announcements: Mapped[bool] = mapped_column(server_default="True")

    ticket: Mapped[Optional[Ticket]] = relationship(foreign_keys="Ticket.used_by_id")

    achievements_count = column_property(
        select(func.count())
        .where(ReceivedAchievement.user_id == id)
        .correlate_except(ReceivedAchievement)
        .scalar_subquery(),
        deferred=True,
    )
    received_achievements: WriteOnlyMapped[Achievement] = relationship(
        secondary="received_achievements",
        passive_deletes=True,
    )

    def to_dto(self) -> UserDTO:
        return UserDTO(
            id=self.id,
            username=self.username,
            role=self.role,
            items_per_page=self.items_per_page,
            receive_all_announcements=self.receive_all_announcements,
        )

    def to_full_dto(self) -> FullUserDTO:
        return FullUserDTO(
            id=self.id,
            username=self.username,
            role=self.role,
            items_per_page=self.items_per_page,
            receive_all_announcements=self.receive_all_announcements,
            ticket=self.ticket.to_dto() if self.ticket else None,
        )

    def __str__(self):
        return f"{self.username} ({self.id})"
