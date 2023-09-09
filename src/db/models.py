from sqlalchemy import (
    BigInteger,
    ForeignKey,
    MetaData,
    Sequence,
    func,
    select,
)
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import (
    Mapped,
    WriteOnlyMapped,
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

    id: Mapped[str] = mapped_column(primary_key=True, unique=True)
    role: Mapped[str] = mapped_column(server_default="visitor")
    used_by: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=True
    )
    issued_by: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )


class ReceivedAchievement(Base):
    __tablename__ = "received_achievements"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    achievement_id: Mapped[int] = mapped_column(
        ForeignKey("achievements.id", ondelete="CASCADE")
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, unique=True, autoincrement=False
    )
    username: Mapped[str] = mapped_column(index=True)
    role: Mapped[str] = mapped_column(server_default="visitor")

    points: Mapped[int] = mapped_column(server_default="0")

    items_per_page: Mapped[int] = mapped_column(nullable=False, server_default="5")
    receive_all_announcements: Mapped[bool] = mapped_column(server_default="False")

    achievements_count = column_property(
        select(func.count()).where(ReceivedAchievement.user_id == id).scalar_subquery(),
    )

    def __str__(self):
        return (
            f"""User: id={str(self.id)}, username={self.username}, role={self.role}"""
        )


class Vote(Base):
    __tablename__ = "votes"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    participant_id: Mapped[int] = mapped_column(
        ForeignKey("participants.id", ondelete="CASCADE")
    )

    participant: Mapped["Participant"] = relationship(lazy="selectin")

    def __str__(self):
        return f"Vote: {self.id} {self.participant_id} {self.participant.nomination.id}"


class Participant(Base):
    __tablename__ = "participants"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True, autoincrement=True)
    title: Mapped[str] = mapped_column(unique=True, index=True)
    nomination_id: Mapped[str] = mapped_column(
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


class Event(Base):
    __tablename__ = "schedule"

    position_sequence = Sequence("schedule_position_seq", start=1)

    id: Mapped[int] = mapped_column(primary_key=True, unique=True, autoincrement=True)
    position: Mapped[int] = mapped_column(
        unique=True, server_default=position_sequence.next_value()
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
        return f"""Event: {str(self.id)}, {self.participant_id}"""


class Nomination(Base):
    __tablename__ = "nominations"

    id: Mapped[str] = mapped_column(primary_key=True, unique=True, autoincrement=False)
    title: Mapped[str] = mapped_column(unique=True, index=True)
    votable: Mapped[bool] = mapped_column(server_default="False")


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True, autoincrement=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("schedule.id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    counter: Mapped[int] = mapped_column(server_default="5")

    event: Mapped["Event"] = relationship(lazy="selectin")


class Settings(Base):
    __tablename__ = "settings"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True, server_default="1")
    voting_enabled: Mapped[bool] = mapped_column(server_default="False")
    announcement_timestamp: Mapped[float] = mapped_column(server_default="0")


class Achievement(Base):
    __tablename__ = "achievements"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column(nullable=True)

    achievement_count = column_property(select(func.count(id)).scalar_subquery())


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    from_user: Mapped[int] = mapped_column(ForeignKey(User.id, ondelete="CASCADE"))
    to_user: Mapped[int] = mapped_column(ForeignKey(User.id, ondelete="CASCADE"))

    points_added: Mapped[int] = mapped_column(nullable=True)
    achievement_added: Mapped[int] = mapped_column(
        ForeignKey(Achievement.id, ondelete="CASCADE"), nullable=True
    )
