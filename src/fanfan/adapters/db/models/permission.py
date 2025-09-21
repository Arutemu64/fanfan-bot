import typing

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fanfan.adapters.db.models.base import Base
from fanfan.core.models.permission import Permission, UserPermission
from fanfan.core.vo.permission import (
    PermissionId,
    PermissionName,
    PermissionObjectId,
    PermissionObjectType,
    UserPermissionId,
)
from fanfan.core.vo.user import UserId

if typing.TYPE_CHECKING:
    from fanfan.adapters.db.models import UserORM  # noqa


class UserPermissionORM(Base):
    __tablename__ = "user_permissions"
    __table_args__ = (
        UniqueConstraint("user_id", "permission_id", "object_id", "object_type"),
    )

    id: Mapped[UserPermissionId] = mapped_column(primary_key=True)

    user_id: Mapped[UserId] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    permission_id: Mapped[PermissionId] = mapped_column(
        ForeignKey("permissions.id", ondelete="CASCADE")
    )

    object_id: Mapped[PermissionObjectId | None] = mapped_column()
    object_type: Mapped[PermissionObjectType | None] = mapped_column()

    user: Mapped["UserORM"] = relationship()
    permission: Mapped["PermissionORM"] = relationship()

    @classmethod
    def from_model(cls, model: UserPermission):
        return UserPermissionORM(
            id=model.id,
            permission_id=model.permission_id,
            user_id=model.user_id,
            object_type=model.object_type,
            object_id=model.object_id,
        )

    def to_model(self) -> UserPermission:
        return UserPermission(
            id=self.id,
            permission_id=self.permission_id,
            user_id=self.user_id,
            object_type=self.object_type,
            object_id=self.object_id,
        )


class PermissionORM(Base):
    __tablename__ = "permissions"

    id: Mapped[PermissionId] = mapped_column(primary_key=True)
    name: Mapped[PermissionName] = mapped_column(unique=True)

    @classmethod
    def from_model(cls, model: Permission):
        return PermissionORM(
            id=model.id,
            name=model.name,
        )

    def to_model(self) -> Permission:
        return Permission(
            id=self.id,
            name=self.name,
        )
