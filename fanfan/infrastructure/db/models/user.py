from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

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
from fanfan.infrastructure.db.models.user_permissions import UserPermissions
from fanfan.infrastructure.db.models.user_settings import UserSettings

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

    settings: Mapped[UserSettings] = relationship()
    permissions: Mapped[UserPermissions] = relationship()
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
        return UserDTO.model_validate(self)

    def to_full_dto(self) -> FullUserDTO:
        return FullUserDTO.model_validate(self)

    def __init__(self, **kw: Any):
        super().__init__(**kw)
        self.permissions = UserPermissions()
        self.settings = UserSettings()

    def __str__(self):
        return f"{self.username} ({self.id})"
