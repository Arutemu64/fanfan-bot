from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fanfan.infrastructure.db.models.base import Base
from fanfan.infrastructure.db.models.user import User


class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    text: Mapped[str] = mapped_column()

    contact_agreement: Mapped[bool] = mapped_column()
    asap: Mapped[bool] = mapped_column()  # Like, ASAP!!!

    user: Mapped[User] = relationship()
