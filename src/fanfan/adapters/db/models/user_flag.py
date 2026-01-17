from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from fanfan.adapters.db.models.base import Base
from fanfan.core.models.user_flag import UserFlag
from fanfan.core.vo.user_flag import UserFlagId
from fanfan.core.vo.user import UserId


class UserFlagORM(Base):
    __tablename__ = "flags"

    id: Mapped[UserFlagId] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    user_id: Mapped[UserId] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    def to_model(self) -> UserFlag:
        return UserFlag(
            id=self.id,
            name=self.name,
            user_id=self.user_id,
        )

    @classmethod
    def from_model(cls, model: UserFlag):
        return UserFlagORM(
            id=model.id,
            name=model.name,
            user_id=model.user_id,
        )
