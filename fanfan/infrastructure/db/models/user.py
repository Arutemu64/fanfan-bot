import typing

from sqlalchemy import BigInteger, func, select
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import (
    Mapped,
    WriteOnlyMapped,
    column_property,
    mapped_column,
    relationship,
)

from fanfan.application.dto.user import FullUserDTO, UserDTO
from fanfan.common.enums import UserRole
from fanfan.infrastructure.db.models import ReceivedAchievement
from fanfan.infrastructure.db.models.base import Base

if typing.TYPE_CHECKING:
    from fanfan.infrastructure.db.models.achievement import Achievement
    from fanfan.infrastructure.db.models.ticket import Ticket


class User(Base):
    __tablename__ = "users"

    def __str__(self):
        return f"{self.username} ({self.id})"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    username: Mapped[str] = mapped_column(index=True, unique=False, nullable=True)
    role: Mapped[UserRole] = mapped_column(
        postgresql.ENUM(UserRole), default=UserRole.VISITOR, server_default="VISITOR"
    )

    items_per_page: Mapped[int] = mapped_column(server_default="5")
    receive_all_announcements: Mapped[bool] = mapped_column(server_default="False")

    ticket: Mapped["Ticket"] = relationship(
        foreign_keys="Ticket.used_by_id", lazy="noload"
    )

    points: Mapped[int] = mapped_column(server_default="0")
    achievements_count = column_property(
        select(func.count())
        .where(ReceivedAchievement.user_id == id)
        .correlate_except(ReceivedAchievement)
        .scalar_subquery(),
        deferred=True,
    )
    received_achievements: WriteOnlyMapped["Achievement"] = relationship(
        secondary="received_achievements"
    )

    def to_dto(self) -> UserDTO:
        return UserDTO.model_validate(self)

    def to_full_dto(self) -> FullUserDTO:
        return FullUserDTO.model_validate(self)