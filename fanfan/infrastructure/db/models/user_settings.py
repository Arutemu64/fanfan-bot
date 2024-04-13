from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from fanfan.infrastructure.db.models.base import Base


class UserSettings(Base):
    __tablename__ = "user_settings"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    items_per_page: Mapped[int] = mapped_column(server_default="5")
    receive_all_announcements: Mapped[bool] = mapped_column(server_default="True")
