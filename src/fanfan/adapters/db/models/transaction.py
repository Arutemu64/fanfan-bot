from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fanfan.adapters.db.models.base import Base
from fanfan.adapters.db.models.user import UserORM
from fanfan.core.models.transaction import Transaction
from fanfan.core.vo.transaction import TransactionId
from fanfan.core.vo.user import UserId


class TransactionORM(Base):
    __tablename__ = "transactions"

    id: Mapped[TransactionId] = mapped_column(primary_key=True)
    points: Mapped[int] = mapped_column()
    comment: Mapped[str | None] = mapped_column()

    # To user
    to_user_id: Mapped[UserId] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    to_user: Mapped[UserORM] = relationship(foreign_keys=to_user_id)

    # From user
    from_user_id: Mapped[UserId | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL")
    )
    from_user: Mapped[UserORM | None] = relationship(foreign_keys=from_user_id)

    @classmethod
    def from_model(cls, model: Transaction):
        return TransactionORM(
            id=model.id,
            points=model.points,
            comment=model.comment,
            to_user_id=model.to_user_id,
            from_user_id=model.from_user_id,
        )

    def to_model(self) -> Transaction:
        return Transaction(
            id=self.id,
            points=self.points,
            comment=self.comment,
            to_user_id=self.to_user_id,
            from_user_id=self.from_user_id,
        )
