import datetime
from typing import List

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    MetaData,
    Sequence,
    func,
    select,
)
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import (
    Mapped,
    as_declarative,
    column_property,
    declared_attr,
    mapped_column,
    relationship,
    validates,
)

from src.bot.structures import UserRole

metadata = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
)


@as_declarative(metadata=metadata)
class Base(AsyncAttrs):
    """Abstract model with declarative base functionality."""

    id: Mapped[int | str]
    time_created: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    time_updated: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), server_default=func.now()
    )

    @classmethod
    @declared_attr
    def __tablename__(cls):
        """Hooks __tablename__ attribute based on model name.

        You can skip specifying this attribute in models, then name for table
        will be got from the model's name.
        """
        return cls.__name__.lower()

    __allow_unmapped__ = False


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[str] = mapped_column(primary_key=True)
    role: Mapped[int] = mapped_column(
        postgresql.ENUM(UserRole), server_default="VISITOR"
    )
    used_by_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )
    issued_by_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    used_by: Mapped["User"] = relationship(lazy="selectin", foreign_keys=used_by_id)
    issued_by: Mapped["User"] = relationship(foreign_keys=issued_by_id)

    def __str__(self):
        return self.id


class ReceivedAchievement(Base):
    __tablename__ = "received_achievements"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    achievement_id: Mapped[int] = mapped_column(
        ForeignKey("achievements.id", ondelete="CASCADE")
    )

    user: Mapped["User"] = relationship(viewonly=True)
    achievement: Mapped["Achievement"] = relationship(viewonly=True)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    username: Mapped[str] = mapped_column(index=True, unique=False, nullable=True)
    role: Mapped[UserRole] = mapped_column(
        postgresql.ENUM(UserRole), server_default="VISITOR"
    )
    items_per_page: Mapped[int] = mapped_column(server_default="5")
    receive_all_announcements: Mapped[bool] = mapped_column(server_default="False")
    points: Mapped[int] = mapped_column(server_default="0")

    received_achievements: Mapped[List["Achievement"]] = relationship(
        secondary="received_achievements"
    )

    achievements_count = column_property(
        select(func.count())
        .where(ReceivedAchievement.user_id == id)
        .correlate_except(ReceivedAchievement)
        .scalar_subquery(),
    )

    def __str__(self):
        return f"{self.username} ({self.id})"


class Event(Base):
    __tablename__ = "schedule"

    position_sequence = Sequence("schedule_position_seq", start=1)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    position: Mapped[float] = mapped_column(
        unique=True, nullable=False, server_default=position_sequence.next_value()
    )
    real_position: Mapped[int] = mapped_column(unique=True, nullable=True)
    participant_id: Mapped[int] = mapped_column(
        ForeignKey("participants.id", ondelete="CASCADE"), nullable=True
    )
    title: Mapped[str] = mapped_column(nullable=True, index=True)
    skip: Mapped[bool] = mapped_column(nullable=True, server_default="False")
    current: Mapped[bool] = mapped_column(nullable=True, unique=True)

    participant: Mapped["Participant"] = relationship(lazy="selectin")

    @validates("real_position")
    def block_real_position_modification(self, key, value):
        raise ValueError(
            "Real position can't be modified since "
            "it's automatically updated by PSQL trigger"
            "(check Alembic files for more details)."
        )

    def __str__(self):
        return self.title


class Achievement(Base):
    __tablename__ = "achievements"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column(nullable=True)

    def __str__(self):
        return self.title


class Vote(Base):
    __tablename__ = "votes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    participant_id: Mapped[int] = mapped_column(
        ForeignKey("participants.id", ondelete="CASCADE")
    )

    user: Mapped["User"] = relationship()
    participant: Mapped["Participant"] = relationship()


class Participant(Base):
    __tablename__ = "participants"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(unique=True, index=True)
    nomination_id: Mapped[str] = mapped_column(
        ForeignKey("nominations.id", ondelete="SET NULL"), nullable=True
    )

    event: Mapped["Event"] = relationship(back_populates="participant")
    nomination: Mapped["Nomination"] = relationship(lazy="selectin")

    votes_count = column_property(
        select(func.count())
        .where(Vote.participant_id == id)
        .correlate_except(Vote)
        .scalar_subquery(),
    )

    def __str__(self):
        return self.title


class Nomination(Base):
    __tablename__ = "nominations"

    id: Mapped[str] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(unique=True)
    votable: Mapped[bool] = mapped_column(server_default="False")

    participants_count = column_property(
        select(func.count())
        .where(Participant.nomination_id == id)
        .correlate_except(Participant)
        .scalar_subquery(),
    )

    def __str__(self):
        return self.title


class Settings(Base):
    __tablename__ = "settings"

    id: Mapped[int] = mapped_column(primary_key=True, server_default="1")
    voting_enabled: Mapped[bool] = mapped_column(server_default="False")
    announcement_timestamp: Mapped[float] = mapped_column(server_default="0")


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("schedule.id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    counter: Mapped[int] = mapped_column(server_default="5")

    user: Mapped["User"] = relationship()
    event: Mapped["Event"] = relationship(lazy="selectin")


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    from_user_id: Mapped[int] = mapped_column(ForeignKey(User.id, ondelete="CASCADE"))
    to_user_id: Mapped[int] = mapped_column(ForeignKey(User.id, ondelete="CASCADE"))
    points_added: Mapped[int] = mapped_column(nullable=True)
    achievement_id_added: Mapped[int] = mapped_column(
        ForeignKey(Achievement.id, ondelete="CASCADE"), nullable=True
    )

    from_user: Mapped["User"] = relationship(foreign_keys=from_user_id)
    to_user: Mapped["User"] = relationship(foreign_keys=to_user_id)

    achievement_added: Mapped["Achievement"] = relationship()
