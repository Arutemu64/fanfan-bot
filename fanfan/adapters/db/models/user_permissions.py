import typing

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fanfan.adapters.db.models.base import Base
from fanfan.core.models.permissions import UserPermissions
from fanfan.core.models.user import UserId

if typing.TYPE_CHECKING:
    from fanfan.adapters.db.models import UserORM


class UserPermissionsORM(Base):
    __tablename__ = "user_permissions"

    # Feedback
    can_send_feedback: Mapped[bool] = mapped_column(server_default="True")

    # Helper specific
    helper_can_edit_schedule: Mapped[bool] = mapped_column(server_default="False")

    # User relation
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    user: Mapped["UserORM"] = relationship(back_populates="permissions")

    def to_model(self) -> UserPermissions:
        return UserPermissions(
            user_id=UserId(self.user_id),
            can_send_feedback=self.can_send_feedback,
            helper_can_edit_schedule=self.helper_can_edit_schedule,
        )
