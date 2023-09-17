import datetime

from flask_login import UserMixin
from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    MetaData,
    Sequence,
    func,
    select,
)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import (
    Mapped,
    WriteOnlyMapped,
    as_declarative,
    column_property,
    declared_attr,
    mapped_column,
    relationship,
)

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
class Base:
    """Abstract model with declarative base functionality."""

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
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

    number: Mapped[str] = mapped_column(unique=True)
    role: Mapped[str] = mapped_column(server_default="visitor")

    used_by_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )
    issued_by_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    used_by: Mapped["User"] = relationship(lazy="selectin", foreign_keys=used_by_id)
    issued_by: Mapped["User"] = relationship(lazy="selectin", foreign_keys=issued_by_id)

    def __str__(self):
        return self.number


class ReceivedAchievement(Base):
    __tablename__ = "received_achievements"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    achievement_id: Mapped[int] = mapped_column(
        ForeignKey("achievements.id", ondelete="CASCADE")
    )

    user: Mapped["User"] = relationship(lazy="selectin", foreign_keys=user_id)
    achievement: Mapped["Achievement"] = relationship(
        lazy="selectin", foreign_keys=achievement_id
    )


class User(Base, UserMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    username: Mapped[str] = mapped_column(index=True, unique=False, nullable=True)

    role: Mapped[str] = mapped_column(server_default="visitor")

    points: Mapped[int] = mapped_column(server_default="0")

    items_per_page: Mapped[int] = mapped_column(server_default="5")
    receive_all_announcements: Mapped[bool] = mapped_column(server_default="False")

    achievements_count = column_property(
        select(func.count()).where(ReceivedAchievement.user_id == id).scalar_subquery(),
        deferred=True,
    )

    def __str__(self):
        return f"{self.username} ({self.id})"


class Event(Base):
    __tablename__ = "schedule"

    position_sequence = Sequence("schedule_position_seq", start=1)

    position: Mapped[int] = mapped_column(
        unique=True, nullable=False, server_default=position_sequence.next_value()
    )
    real_position: Mapped[int] = mapped_column(
        unique=True, nullable=True
    )  # Обновляется триггером в БД, не забывать делать
    # refresh после изменения position или skip
    participant_id: Mapped[int] = mapped_column(
        ForeignKey("participants.id", ondelete="CASCADE"), nullable=True
    )
    title: Mapped[str] = mapped_column(nullable=True)
    current: Mapped[bool] = mapped_column(nullable=True, unique=True)
    skip: Mapped[bool] = mapped_column(nullable=True, server_default="False")

    participant: Mapped["Participant"] = relationship(lazy="selectin", viewonly=True)

    @hybrid_property
    def joined_title(self) -> str:
        return self.title or self.participant.title

    def __str__(self):
        return self.joined_title


class Achievement(Base):
    __tablename__ = "achievements"

    title: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column(nullable=True)

    def __str__(self):
        return self.title


class Vote(Base):
    __tablename__ = "votes"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    participant_id: Mapped[int] = mapped_column(
        ForeignKey("participants.id", ondelete="CASCADE")
    )

    user: Mapped["User"] = relationship(lazy="selectin")
    participant: Mapped["Participant"] = relationship(lazy="selectin")


class Participant(Base):
    __tablename__ = "participants"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(unique=True, index=True)
    nomination_id: Mapped[int] = mapped_column(
        ForeignKey("nominations.id", ondelete="SET NULL"), nullable=True
    )

    event: WriteOnlyMapped["Event"] = relationship(
        lazy="write_only", cascade="all, delete-orphan", viewonly=True
    )
    nomination: Mapped["Nomination"] = relationship(lazy="selectin")

    votes_count = column_property(
        select(func.count()).where(Vote.participant_id == id).scalar_subquery(),
        deferred=True,
    )


class Nomination(Base):
    __tablename__ = "nominations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(unique=True)
    title: Mapped[str] = mapped_column(unique=True)
    votable: Mapped[bool] = mapped_column(server_default="False")

    participants_count = column_property(
        select(func.count()).where(Participant.nomination_id == id).scalar_subquery(),
        deferred=True,
    )

    def __str__(self):
        return self.title


class Settings(Base):
    __tablename__ = "settings"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True, server_default="1")
    voting_enabled: Mapped[bool] = mapped_column(server_default="False")
    announcement_timestamp: Mapped[float] = mapped_column(server_default="0")


class Subscription(Base):
    __tablename__ = "subscriptions"

    event_id: Mapped[int] = mapped_column(ForeignKey("schedule.id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    counter: Mapped[int] = mapped_column(server_default="5")

    event: Mapped["Event"] = relationship(lazy="selectin")


class Transaction(Base):
    __tablename__ = "transactions"

    from_user_id: Mapped[int] = mapped_column(ForeignKey(User.id, ondelete="CASCADE"))
    to_user_id: Mapped[int] = mapped_column(ForeignKey(User.id, ondelete="CASCADE"))

    from_user: Mapped["User"] = relationship(lazy="selectin", foreign_keys=from_user_id)
    to_user: Mapped["User"] = relationship(lazy="selectin", foreign_keys=to_user_id)

    points_added: Mapped[int] = mapped_column(nullable=True)
    achievement_id_added: Mapped[int] = mapped_column(
        ForeignKey(Achievement.id, ondelete="CASCADE"), nullable=True
    )

    achievement_added: Mapped["Achievement"] = relationship(
        lazy="selectin", foreign_keys=achievement_id_added
    )
