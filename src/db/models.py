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


class User(Base):
    __tablename__ = "users"

    ticket_id: Mapped[str] = mapped_column(primary_key=True, unique=True, nullable=True)
    tg_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, autoincrement=False, nullable=True
    )
    username: Mapped[str] = mapped_column(nullable=True)
    role: Mapped[str] = mapped_column(server_default="visitor")

    votes: Mapped[List["Vote"]] = relationship(lazy="selectin")

    def __str__(self):
        return f"""User: tg_id={str(self.tg_id)}, username={self.username}, role={self.role}"""


class Event(Base):
    __tablename__ = "schedule"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True, autoincrement=True)
    participant_id: Mapped[int] = mapped_column(
        ForeignKey("participants.id"), nullable=True
    )
    title: Mapped[str] = mapped_column(nullable=True)
    current: Mapped[bool] = mapped_column(nullable=True, unique=True)
    next: Mapped[bool] = mapped_column(nullable=True, unique=True)

    participant: Mapped["Participant"] = relationship(lazy="selectin")

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
    event: Mapped["Event"] = relationship(lazy="selectin", cascade="all, delete-orphan")


class Nomination(Base):
    __tablename__ = "nominations"

    id: Mapped[str] = mapped_column(primary_key=True, unique=True, autoincrement=False)
    title: Mapped[str] = mapped_column(unique=True)
    votable: Mapped[bool] = mapped_column(server_default="False")

    participants: WriteOnlyMapped["Participant"] = relationship(
        order_by=Participant.id.asc(), cascade="all, delete-orphan"
    )


class Settings(Base):
    __tablename__ = "settings"

    voting_enabled: Mapped[bool] = mapped_column(primary_key=True)


class Vote(Base):
    __tablename__ = "votes"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(ForeignKey("users.tg_id"))
    participant_id: Mapped[int] = mapped_column(ForeignKey("participants.id"))

    participant: Mapped["Participant"] = relationship(lazy="selectin")

    def __str__(self):
        return f"Vote: {self.tg_id} {self.participant_id} {self.nomination_id}"
