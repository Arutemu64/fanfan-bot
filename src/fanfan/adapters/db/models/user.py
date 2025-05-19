from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, func, select
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import (
    Mapped,
    column_property,
    declared_attr,
    mapped_column,
    relationship,
)

from fanfan.adapters.db.models.base import Base
from fanfan.adapters.db.models.received_achievement import ReceivedAchievementORM
from fanfan.adapters.db.models.user_permissions import UserPermissionsORM
from fanfan.adapters.db.models.user_settings import UserSettingsORM
from fanfan.core.models.user import User
from fanfan.core.vo.user import UserId, UserRole

if TYPE_CHECKING:
    from fanfan.adapters.db.models.ticket import TicketORM


class UserORM(Base):
    __tablename__ = "users"

    id: Mapped[UserId] = mapped_column(
        BigInteger, primary_key=True, autoincrement=False
    )
    username: Mapped[str | None] = mapped_column(index=True, unique=True)

    first_name: Mapped[str | None] = mapped_column()
    last_name: Mapped[str | None] = mapped_column()

    role: Mapped[UserRole] = mapped_column(
        postgresql.ENUM(UserRole),
        default=UserRole.VISITOR,
        server_default="VISITOR",
    )

    # Relations
    settings: Mapped[UserSettingsORM] = relationship(cascade="all, delete-orphan")
    permissions: Mapped[UserPermissionsORM] = relationship(cascade="all, delete-orphan")
    ticket: Mapped[TicketORM | None] = relationship(foreign_keys="TicketORM.used_by_id")

    # Quest
    points: Mapped[int] = mapped_column(server_default="0", deferred=True)
    achievements_count = column_property(
        select(func.count(ReceivedAchievementORM.id))
        .where(ReceivedAchievementORM.user_id == id)
        .correlate_except(ReceivedAchievementORM)
        .scalar_subquery(),
        deferred=True,
    )

    @declared_attr
    @classmethod
    def rank(cls) -> Mapped[int | None]:
        order_rule = (cls.points + cls.achievements_count).desc()
        where_rule = (cls.points + cls.achievements_count) > 0
        rank_subquery = (
            select(
                cls.id,
                func.row_number().over(order_by=order_rule).label("rank"),
            )
            .where(where_rule)
            .subquery()
        )
        stmt = select(rank_subquery.c.rank).where(rank_subquery.c.id == cls.id)
        return column_property(
            stmt.scalar_subquery(),
            expire_on_flush=True,
            deferred=True,
        )

    def __str__(self) -> str:
        return f"{self.username} ({self.id})"

    @classmethod
    def from_model(cls, model: User):
        return UserORM(
            id=model.id,
            username=model.username,
            first_name=model.first_name,
            last_name=model.last_name,
            role=model.role,
            permissions=UserPermissionsORM.from_model(model.permissions),
            settings=UserSettingsORM.from_model(model.settings),
        )

    def to_model(self) -> User:
        return User(
            id=UserId(self.id),
            username=self.username,
            first_name=self.first_name,
            last_name=self.last_name,
            role=UserRole(self.role),
            permissions=self.permissions.to_model(),
            settings=self.settings.to_model(),
        )
