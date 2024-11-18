from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy import BigInteger, func, select
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import (
    Mapped,
    column_property,
    mapped_column,
    relationship,
)

from fanfan.adapters.db.models.base import Base
from fanfan.adapters.db.models.quest_registration import QuestRegistration
from fanfan.adapters.db.models.received_achievement import ReceivedAchievement
from fanfan.adapters.db.models.user_permissions import UserPermissions
from fanfan.adapters.db.models.user_settings import UserSettings
from fanfan.core.enums import UserRole
from fanfan.core.models.user import FullUserModel, UserId, UserModel

if TYPE_CHECKING:
    from fanfan.adapters.db.models.ticket import Ticket


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    username: Mapped[str | None] = mapped_column(index=True, unique=True)

    first_name: Mapped[str | None] = mapped_column()
    last_name: Mapped[str | None] = mapped_column()

    role: Mapped[UserRole] = mapped_column(
        postgresql.ENUM(UserRole),
        default=UserRole.VISITOR,
        server_default="VISITOR",
    )

    # Relations
    settings: Mapped[UserSettings] = relationship(cascade="all, delete-orphan")
    permissions: Mapped[UserPermissions] = relationship(cascade="all, delete-orphan")
    ticket: Mapped[Ticket | None] = relationship(foreign_keys="Ticket.used_by_id")

    # Quest
    quest_registration: Mapped[QuestRegistration | None] = relationship()
    points: Mapped[int] = mapped_column(server_default="0", deferred=True)
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

    @classmethod
    def from_model(cls, model: UserModel):
        return User(
            id=model.id,
            username=model.username,
            first_name=model.first_name,
            last_name=model.last_name,
            role=model.role,
        )

    def to_model(self) -> UserModel:
        return UserModel(
            id=UserId(self.id),
            username=self.username,
            first_name=self.first_name,
            last_name=self.last_name,
            role=UserRole(self.role),
        )

    def to_full_model(self) -> FullUserModel:
        return FullUserModel(
            id=UserId(self.id),
            username=self.username,
            first_name=self.first_name,
            last_name=self.last_name,
            role=UserRole(self.role),
            permissions=self.permissions.to_model(),
            settings=self.settings.to_model(),
            ticket=self.ticket.to_model() if self.ticket else None,
        )
