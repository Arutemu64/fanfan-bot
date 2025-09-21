from sqlalchemy import ForeignKey
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fanfan.adapters.db.models.base import Base
from fanfan.adapters.db.models.schedule_event import ScheduleEventORM
from fanfan.adapters.db.models.user import UserORM
from fanfan.core.models.schedule_change import (
    ScheduleChange,
    ScheduleChangeType,
)
from fanfan.core.vo.schedule_change import ScheduleChangeId
from fanfan.core.vo.schedule_event import ScheduleEventId
from fanfan.core.vo.user import UserId


class ScheduleChangeORM(Base):
    __tablename__ = "schedule_changes"

    id: Mapped[ScheduleChangeId] = mapped_column(primary_key=True)

    # Arguments
    type: Mapped[ScheduleChangeType] = mapped_column(
        postgresql.ENUM(ScheduleChangeType)
    )
    changed_event_id: Mapped[ScheduleEventId | None] = mapped_column(
        ForeignKey("schedule.id", ondelete="CASCADE")
    )

    argument_event_id: Mapped[ScheduleEventId | None] = mapped_column(
        ForeignKey("schedule.id", ondelete="CASCADE")
    )
    user_id: Mapped[UserId | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
    )
    send_global_announcement: Mapped[bool] = mapped_column()
    mailing_id: Mapped[str | None] = mapped_column()

    # Relationships
    changed_event: Mapped[ScheduleEventORM | None] = relationship(
        foreign_keys=changed_event_id
    )
    argument_event: Mapped[ScheduleEventORM | None] = relationship(
        foreign_keys=argument_event_id
    )
    user: Mapped[UserORM | None] = relationship(foreign_keys=user_id)

    @classmethod
    def from_model(cls, model: ScheduleChange):
        return ScheduleChangeORM(
            id=model.id,
            type=model.type,
            mailing_id=model.mailing_id,
            user_id=model.user_id,
            changed_event_id=model.changed_event_id,
            argument_event_id=model.argument_event_id,
            send_global_announcement=model.send_global_announcement,
        )

    def to_model(self) -> ScheduleChange:
        return ScheduleChange(
            id=self.id,
            type=self.type,
            mailing_id=self.mailing_id,
            user_id=self.user_id,
            changed_event_id=self.changed_event_id,
            argument_event_id=self.argument_event_id,
            send_global_announcement=self.send_global_announcement,
        )
