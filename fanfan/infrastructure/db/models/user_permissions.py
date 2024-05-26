import typing

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fanfan.application.dto.user import UserPermissionsDTO
from fanfan.infrastructure.db.models.base import Base

if typing.TYPE_CHECKING:
    from fanfan.infrastructure.db.models import User


class UserPermissions(Base):
    __tablename__ = "user_permissions"

    can_send_feedback: Mapped[bool] = mapped_column(server_default="True")

    # User elation
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    user: Mapped["User"] = relationship(back_populates="permissions")

    def __str__(self):
        return UserPermissionsDTO.model_validate(self).__str__()
