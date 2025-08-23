from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.orm import Mapped, mapped_column

from fanfan.adapters.db.models.base import Base
from fanfan.core.models.permission import Permission

user_permissions = Table(
    "user_permissions",
    Base.metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column(
        "permission_id",
        ForeignKey("permissions.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class PermissionORM(Base):
    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)

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
