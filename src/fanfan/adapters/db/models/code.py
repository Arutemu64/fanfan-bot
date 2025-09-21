from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fanfan.adapters.db.models.achievement import AchievementORM
from fanfan.adapters.db.models.base import Base
from fanfan.adapters.db.models.ticket import TicketORM
from fanfan.adapters.db.models.user import UserORM
from fanfan.core.models.code import Code
from fanfan.core.vo.achievements import AchievementId
from fanfan.core.vo.code import CodeId
from fanfan.core.vo.ticket import TicketId
from fanfan.core.vo.user import UserId


class CodeORM(Base):
    __tablename__ = "codes"

    id: Mapped[CodeId] = mapped_column(primary_key=True)

    achievement_id: Mapped[AchievementId | None] = mapped_column(
        ForeignKey("achievements.id", ondelete="CASCADE"),
    )
    user_id: Mapped[UserId | None] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
    )
    ticket_id: Mapped[TicketId | None] = mapped_column(
        ForeignKey("tickets.id", ondelete="CASCADE"),
    )

    achievement: Mapped[AchievementORM | None] = relationship(
        foreign_keys=achievement_id
    )
    user: Mapped[UserORM | None] = relationship(foreign_keys=user_id)
    ticket: Mapped[TicketORM | None] = relationship(foreign_keys=ticket_id)

    def to_model(self) -> Code:
        return Code(
            id=self.id,
            achievement_id=self.achievement_id,
            user_id=self.user_id,
            ticket_id=self.ticket_id,
        )

    @classmethod
    def from_model(cls, model: Code):
        return CodeORM(
            id=model.id,
            achievement_id=model.achievement_id,
            user_id=model.user_id,
            ticket_id=model.ticket_id,
        )
