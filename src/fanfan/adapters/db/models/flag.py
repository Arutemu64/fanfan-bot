from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from fanfan.adapters.db.models.base import Base
from fanfan.core.models.flag import Flag
from fanfan.core.vo.flag import FlagId
from fanfan.core.vo.user import UserId


class FlagORM(Base):
    __tablename__ = "flags"

    id: Mapped[int] = mapped_column(primary_key=True)
    flag_name: Mapped[str] = mapped_column()
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    def to_model(self) -> Flag:
        return Flag(
            id=FlagId(self.id),
            flag_name=self.flag_name,
            user_id=UserId(self.user_id),
        )

    @classmethod
    def from_model(cls, model: Flag):
        return FlagORM(
            id=model.id,
            flag_name=model.flag_name,
            user_id=model.user_id,
        )
