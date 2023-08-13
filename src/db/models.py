from typing import List

from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import (
    Mapped,
    WriteOnlyMapped,
    declarative_base,
    mapped_column,
    relationship,
)

Base = declarative_base()


# TODO Если вынести модели в разные файлы, возникает циклический импорт.
#  Придумать что с этим можно сделать. Пока и так неплохо.


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[str] = mapped_column(primary_key=True, unique=True)
    role: Mapped[str] = mapped_column(server_default="visitor")
    used_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    issued_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, unique=True, autoincrement=False
    )
    username: Mapped[str] = mapped_column()
    role: Mapped[str] = mapped_column(server_default="visitor")
    receive_all_announcements: Mapped[bool] = mapped_column(server_default="False")

    votes: WriteOnlyMapped["Vote"] = relationship(lazy="write_only")

    def __str__(self):
        return (
            f"""User: id={str(self.id)}, username={self.username}, role={self.role}"""
        )


class Event(Base):
    __tablename__ = "schedule"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True, autoincrement=True)
    participant_id: Mapped[int] = mapped_column(
        ForeignKey("participants.id"), nullable=True
    )
    title: Mapped[str] = mapped_column(nullable=True)
    current: Mapped[bool] = mapped_column(nullable=True, unique=True)

    participant: Mapped["Participant"] = relationship(lazy="selectin")
    subscriptions: WriteOnlyMapped["Subscription"] = relationship(lazy="write_only")

    def __str__(self):
        return f"""Event: {str(self.id)}, {self.participant_id}"""


class Participant(Base):
    __tablename__ = "participants"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True, autoincrement=True)
    title: Mapped[str] = mapped_column(unique=True)
    nomination_id: Mapped[str] = mapped_column(
        ForeignKey("nominations.id"), nullable=True
    )

    nomination: Mapped["Nomination"] = relationship(lazy="selectin")
    votes: Mapped[List["Vote"]] = relationship(
        lazy="selectin", cascade="all, delete-orphan"
    )


class Nomination(Base):
    __tablename__ = "nominations"

    id: Mapped[str] = mapped_column(primary_key=True, unique=True, autoincrement=False)
    title: Mapped[str] = mapped_column(unique=True)
    votable: Mapped[bool] = mapped_column(server_default="False")

    participants: WriteOnlyMapped["Participant"] = relationship(
        order_by=Participant.id.asc(), cascade="all, delete-orphan"
    )


class Vote(Base):
    __tablename__ = "votes"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    participant_id: Mapped[int] = mapped_column(ForeignKey("participants.id"))

    participant: Mapped["Participant"] = relationship(lazy="selectin")

    def __str__(self):
        return f"Vote: {self.id} {self.participant_id} {self.nomination_id}"


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True, autoincrement=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("schedule.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    counter: Mapped[int] = mapped_column(server_default="5")

    event: Mapped["Event"] = relationship(lazy="selectin")
    user: Mapped["User"] = relationship(lazy="selectin")
