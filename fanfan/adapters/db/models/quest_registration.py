from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from fanfan.adapters.db.models.base import Base


class QuestRegistration(Base):
    __tablename__ = "quest_registrations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True
    )
