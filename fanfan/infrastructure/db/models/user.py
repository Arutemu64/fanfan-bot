from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy import BigInteger, func, select
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import (
    Mapped,
    WriteOnlyMapped,
    column_property,
    mapped_column,
    relationship,
)

from fanfan.core.enums import UserRole
from fanfan.core.models.user import FullUserDTO, UserDTO
from fanfan.infrastructure.db.models.base import Base
from fanfan.infrastructure.db.models.received_achievement import ReceivedAchievement
from fanfan.infrastructure.db.models.user_permissions import UserPermissions
from fanfan.infrastructure.db.models.user_settings import UserSettings

if TYPE_CHECKING:
    from fanfan.infrastructure.db.models import Achievement
    from fanfan.infrastructure.db.models.ticket import Ticket


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    username: Mapped[str | None] = mapped_column(
        index=True,
        unique=False,
        nullable=True,
    )
    role: Mapped[UserRole] = mapped_column(
        postgresql.ENUM(UserRole),
        default=UserRole.VISITOR,
        server_default="VISITOR",
    )

    # Relations
    settings: Mapped[UserSettings] = relationship()
    permissions: Mapped[UserPermissions] = relationship()
    ticket: Mapped[Ticket | None] = relationship(foreign_keys="Ticket.used_by_id")
    received_achievements: WriteOnlyMapped[Achievement] = relationship(
        secondary="received_achievements",
        passive_deletes=True,
    )
    achievements_count = column_property(
        select(func.count(ReceivedAchievement.id))
        .where(ReceivedAchievement.user_id == id)
        .correlate_except(ReceivedAchievement)
        .scalar_subquery(),
        deferred=True,
    )

    def __init__(self, **kw: Any) -> None:
        super().__init__(**kw)
        self.permissions = UserPermissions()
        self.settings = UserSettings()

    def __str__(self) -> str:
        return f"{self.username} ({self.id})"

    def to_dto(self) -> UserDTO:
        return UserDTO(
            id=self.id,
            username=self.username,
            role=self.role,
        )

    def to_full_dto(self) -> FullUserDTO:
        self.ticket: Ticket
        self.settings: UserSettings
        self.permissions: UserPermissions
        return FullUserDTO(
            id=self.id,
            username=self.username,
            role=self.role,
            ticket=self.ticket.to_dto() if self.ticket else None,
            settings=self.settings.to_dto(),
            permissions=self.permissions.to_dto(),
        )
