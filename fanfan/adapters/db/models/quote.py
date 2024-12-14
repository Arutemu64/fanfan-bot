from sqlalchemy.orm import Mapped, mapped_column

from fanfan.adapters.db.models.base import Base


class DBQuote(Base):
    __tablename__ = "quotes"

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column()
