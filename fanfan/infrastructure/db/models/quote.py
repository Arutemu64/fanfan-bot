from sqlalchemy.orm import Mapped, mapped_column

from fanfan.infrastructure.db.models.base import Base


class Quote(Base):
    __tablename__ = "quotes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    text: Mapped[str] = mapped_column()
