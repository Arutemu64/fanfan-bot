import typing

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fanfan.core.models.user import UserPermissionsDTO
from fanfan.infrastructure.db.models.base import Base

if typing.TYPE_CHECKING:
    from fanfan.infrastructure.db.models import User


class UserPermissions(Base):
    __tablename__ = "user_permissions"

    can_send_feedback: Mapped[bool] = mapped_column(server_default="True")

    # User relation
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    user: Mapped["User"] = relationship(back_populates="permissions")

    def to_dto(self) -> UserPermissionsDTO:
        return UserPermissionsDTO(can_send_feedback=self.can_send_feedback)
