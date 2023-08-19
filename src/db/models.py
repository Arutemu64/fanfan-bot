from typing import List

from sqlalchemy import BigInteger, ForeignKey, MetaData, Sequence, func
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.orm import (
    Mapped,
    WriteOnlyMapped,
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


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, unique=True, autoincrement=False
    )
    username: Mapped[str] = mapped_column(index=True)
    role: Mapped[str] = mapped_column(server_default="visitor")
    receive_all_announcements: Mapped[bool] = mapped_column(server_default="False")

    ticket: Mapped["Ticket"] = relationship(
        lazy="selectin", foreign_keys="Ticket.used_by", cascade="all, delete-orphan"
    )
    votes: WriteOnlyMapped["Vote"] = relationship(
        lazy="write_only", passive_deletes=True, cascade="all, delete-orphan"
    )
    subscriptions: WriteOnlyMapped["Subscription"] = relationship(
        lazy="write_only", passive_deletes=True, cascade="all, delete-orphan"
    )

    def __str__(self):
        return (
            f"""User: id={str(self.id)}, username={self.username}, role={self.role}"""
        )


class Event(Base):
    __tablename__ = "schedule"

    position_sequence = Sequence("schedule_position_seq", start=1)

    id: Mapped[int] = mapped_column(primary_key=True, unique=True, autoincrement=True)
    position: Mapped[int] = mapped_column(
        unique=True, server_default=position_sequence.next_value()
    )
    participant_id: Mapped[int] = mapped_column(
        ForeignKey("participants.id", ondelete="CASCADE"), nullable=True
    )
    title: Mapped[str] = mapped_column(nullable=True)
    current: Mapped[bool] = mapped_column(nullable=True, unique=True)
    hidden: Mapped[bool] = mapped_column(nullable=True, server_default="False")

    participant: Mapped["Participant"] = relationship(lazy="selectin")
    subscriptions: WriteOnlyMapped["Subscription"] = relationship(
        lazy="write_only", cascade="all, delete-orphan", passive_deletes=True
    )

    def __str__(self):
        return f"""Event: {str(self.id)}, {self.participant_id}"""


class Participant(Base):
    __tablename__ = "participants"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True, autoincrement=True)
    title: Mapped[str] = mapped_column(unique=True, index=True)
    nomination_id: Mapped[str] = mapped_column(
        ForeignKey("nominations.id", ondelete="SET NULL"), nullable=True
    )

    event: Mapped["Event"] = relationship(lazy="selectin", cascade="all, delete-orphan")
    nomination: Mapped["Nomination"] = relationship(lazy="selectin")
    votes: Mapped[List["Vote"]] = relationship(
        lazy="selectin", cascade="all, delete-orphan"
    )


class Nomination(Base):
    __tablename__ = "nominations"

    id: Mapped[str] = mapped_column(primary_key=True, unique=True, autoincrement=False)
    title: Mapped[str] = mapped_column(unique=True, index=True)
    votable: Mapped[bool] = mapped_column(server_default="False")

    participants: WriteOnlyMapped["Participant"] = relationship(
        order_by=Participant.id.asc()
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


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True, autoincrement=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("schedule.id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    counter: Mapped[int] = mapped_column(server_default="5")

    event: Mapped["Event"] = relationship(lazy="selectin")
    user: Mapped["User"] = relationship(lazy="selectin")
