from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fanfan.infrastructure.db.models.base import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    from_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    to_user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    points_added: Mapped[int] = mapped_column(nullable=True)
    achievement_id_added: Mapped[int] = mapped_column(
        ForeignKey("achievements.id", ondelete="CASCADE"), nullable=True
    )

    from_user: Mapped["User"] = relationship(foreign_keys=from_user_id)  # noqa: F821
    to_user: Mapped["User"] = relationship(foreign_keys=to_user_id)  # noqa: F821

    achievement_added: Mapped["Achievement"] = relationship()  # noqa: F821
