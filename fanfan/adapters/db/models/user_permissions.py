import typing

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fanfan.adapters.db.models.base import Base
from fanfan.core.models.user import UserId, UserPermissionsModel

if typing.TYPE_CHECKING:
    from fanfan.adapters.db.models import User


class UserPermissions(Base):
    __tablename__ = "user_permissions"

    can_send_feedback: Mapped[bool] = mapped_column(server_default="True")

    # User relation
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    user: Mapped["User"] = relationship(back_populates="permissions")

    def to_model(self) -> UserPermissionsModel:
        return UserPermissionsModel(
            user_id=UserId(self.user_id), can_send_feedback=self.can_send_feedback
        )
