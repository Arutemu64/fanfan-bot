from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fanfan.adapters.db.models.base import Base
from fanfan.adapters.db.models.user import UserORM
from fanfan.core.models.feedback import Feedback, FeedbackFull, FeedbackId
from fanfan.core.models.mailing import MailingId
from fanfan.core.models.user import UserId


class FeedbackORM(Base):
    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column()

    # Mailing to orgs
    mailing_id: Mapped[str | None] = mapped_column()

    # User
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
    )
    user: Mapped[UserORM | None] = relationship(foreign_keys=user_id)

    # Processed
    processed_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL")
    )
    processed_by: Mapped[UserORM | None] = relationship(foreign_keys=processed_by_id)

    @classmethod
    def from_model(cls, model: Feedback):
        return FeedbackORM(
            id=model.id,
            text=model.text,
            user_id=model.user_id,
            processed_by_id=model.processed_by_id,
            mailing_id=model.mailing_id,
        )

    def to_model(self) -> Feedback:
        return Feedback(
            id=FeedbackId(self.id),
            text=self.text,
            user_id=UserId(self.user_id),
            processed_by_id=UserId(self.processed_by_id),
            mailing_id=MailingId(self.mailing_id),
        )

    def to_full_model(self) -> FeedbackFull:
        return FeedbackFull(
            id=FeedbackId(self.id),
            text=self.text,
            user_id=UserId(self.user_id),
            processed_by_id=UserId(self.processed_by_id),
            mailing_id=MailingId(self.mailing_id),
            user=self.user.to_model() if self.user else None,
            processed_by=self.processed_by.to_model() if self.processed_by else None,
        )
