from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fanfan.adapters.db.models.base import Base
from fanfan.adapters.db.models.user import User
from fanfan.core.models.feedback import FeedbackId, FeedbackModel
from fanfan.core.models.user import UserId


class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column()
    asap: Mapped[bool] = mapped_column()  # Like, ASAP!!!

    # User relation
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    user: Mapped[User] = relationship()

    def to_model(self) -> FeedbackModel:
        return FeedbackModel(
            id=FeedbackId(self.id),
            user_id=UserId(self.user_id),
            text=self.text,
            asap=self.asap,
        )
