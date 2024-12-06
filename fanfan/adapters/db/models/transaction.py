from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fanfan.adapters.db.models.base import Base
from fanfan.adapters.db.models.user import User
from fanfan.core.models.transaction import TransactionId, TransactionModel
from fanfan.core.models.user import UserId


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    points: Mapped[int] = mapped_column()
    comment: Mapped[str | None] = mapped_column()

    # To user
    to_user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    to_user: Mapped[User] = relationship(foreign_keys=to_user_id)

    # From user
    from_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL")
    )
    from_user: Mapped[User | None] = relationship(foreign_keys=from_user_id)

    @classmethod
    def from_model(cls, model: TransactionModel):
        return Transaction(
            id=model.id,
            points=model.points,
            comment=model.comment,
            to_user_id=model.to_user_id,
            from_user_id=model.from_user_id,
        )

    def to_model(self) -> TransactionModel:
        return TransactionModel(
            id=TransactionId(self.id),
            points=self.points,
            comment=self.comment,
            to_user_id=UserId(self.to_user_id),
            from_user_id=UserId(self.from_user_id),
        )
