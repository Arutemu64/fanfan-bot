from sqlalchemy import ForeignKey
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fanfan.adapters.db.models.base import Base
from fanfan.adapters.db.models.event import EventORM
from fanfan.adapters.db.models.user import UserORM
from fanfan.core.models.event import EventId
from fanfan.core.models.mailing import MailingId
from fanfan.core.models.schedule_change import (
    ScheduleChange,
    ScheduleChangeFull,
    ScheduleChangeId,
    ScheduleChangeType,
)
from fanfan.core.models.user import UserId


class ScheduleChangeORM(Base):
    __tablename__ = "schedule_changes"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Arguments
    type: Mapped[ScheduleChangeType] = mapped_column(
        postgresql.ENUM(ScheduleChangeType)
    )
    changed_event_id: Mapped[int | None] = mapped_column(
        ForeignKey("schedule.id", ondelete="CASCADE")
    )

    argument_event_id: Mapped[int | None] = mapped_column(
        ForeignKey("schedule.id", ondelete="CASCADE")
    )
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
    )
    send_global_announcement: Mapped[bool] = mapped_column()
    mailing_id: Mapped[str | None] = mapped_column()

    # Relationships
    changed_event: Mapped[EventORM | None] = relationship(foreign_keys=changed_event_id)
    argument_event: Mapped[EventORM | None] = relationship(
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
            id=ScheduleChangeId(self.id),
            type=self.type,
            mailing_id=MailingId(self.mailing_id),
            user_id=UserId(self.user_id),
            changed_event_id=EventId(self.changed_event_id),
            argument_event_id=EventId(self.argument_event_id),
            send_global_announcement=self.send_global_announcement,
        )

    def to_full_model(self) -> ScheduleChangeFull:
        return ScheduleChangeFull(
            id=ScheduleChangeId(self.id),
            type=self.type,
            user_id=UserId(self.user_id),
            mailing_id=MailingId(self.mailing_id),
            changed_event_id=EventId(self.changed_event_id),
            argument_event_id=EventId(self.argument_event_id),
            user=self.user.to_model() if self.user else None,
            changed_event=self.changed_event.to_full_model()
            if self.changed_event
            else None,
            argument_event=self.argument_event.to_full_model()
            if self.argument_event
            else None,
            send_global_announcement=self.send_global_announcement,
        )
