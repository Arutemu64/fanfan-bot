from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from fanfan.adapters.db.models.base import Base
from fanfan.core.models.contest import ContestEntry, ContestEntryId
from fanfan.core.models.user import UserId


class ContestEntryORM(Base):
    __tablename__ = "contest_entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    contest_name: Mapped[str] = mapped_column()
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    def to_model(self) -> ContestEntry:
        return ContestEntry(
            id=ContestEntryId(self.id),
            contest_name=self.contest_name,
            user_id=UserId(self.user_id),
        )

    @classmethod
    def from_model(cls, model: ContestEntry):
        return ContestEntryORM(
            id=model.id,
            contest_name=model.contest_name,
            user_id=model.user_id,
        )
