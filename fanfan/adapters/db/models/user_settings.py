import typing

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fanfan.adapters.db.models.base import Base
from fanfan.core.models.user import UserId, UserSettingsModel

if typing.TYPE_CHECKING:
    from fanfan.adapters.db.models import User


class UserSettings(Base):
    __tablename__ = "user_settings"

    items_per_page: Mapped[int] = mapped_column(server_default="5")
    receive_all_announcements: Mapped[bool] = mapped_column(server_default="True")

    # User relation
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    user: Mapped["User"] = relationship(back_populates="settings")

    def to_model(self) -> UserSettingsModel:
        return UserSettingsModel(
            user_id=UserId(self.user_id),
            items_per_page=self.items_per_page,
            receive_all_announcements=self.receive_all_announcements,
        )
