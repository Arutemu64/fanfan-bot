from typing import List

from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, relationship

from bot.db.requests import Requests

Base = declarative_base()


class User(Requests, Base):
    __tablename__ = "users"

    ticket_id: Mapped[str] = mapped_column(primary_key=True, unique=True, nullable=True)
    tg_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, autoincrement=False, nullable=True
    )
    username: Mapped[str] = mapped_column(nullable=True)
    role: Mapped[str] = mapped_column(server_default="visitor")

    votes: Mapped[List["Vote"]] = relationship()

    def __str__(self):
        return f"""User: tg_id={str(self.tg_id)}, username={self.username}, role={self.role}"""


class Nomination(Requests, Base):
    __tablename__ = "nominations"

    id: Mapped[str] = mapped_column(primary_key=True, unique=True, autoincrement=False)
    title: Mapped[str] = mapped_column(unique=True)
    votable: Mapped[bool] = mapped_column(server_default="False")

    participants: Mapped[List["Participant"]] = relationship(lazy="selectin")


class Participant(Requests, Base):
    __tablename__ = "participants"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True, autoincrement=True)
    title: Mapped[str] = mapped_column(unique=True)
    nomination_id: Mapped[str] = mapped_column(
        ForeignKey("nominations.id"), nullable=True
    )

    nomination: Mapped["Nomination"] = relationship(lazy="joined")
    votes: Mapped[List["Vote"]] = relationship(lazy="selectin")


class Event(Requests, Base):
    __tablename__ = "schedule"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True, autoincrement=True)
    participant_id: Mapped[int] = mapped_column(ForeignKey("participants.id"))
    text: Mapped[str] = mapped_column(nullable=True)
    current: Mapped[bool] = mapped_column(nullable=True, unique=True)
    next: Mapped[bool] = mapped_column(nullable=True, unique=True)

    def __str__(self):
        return f"""Event: {str(self.id)}, {self.participant_id}"""

    participant: Mapped["Participant"] = relationship(lazy="selectin")


class Vote(Requests, Base):
    __tablename__ = "votes"

    vote_id: Mapped[int] = mapped_column(
        primary_key=True, unique=True, autoincrement=True
    )
    tg_id: Mapped[int] = mapped_column(ForeignKey("users.tg_id"))
    participant_id: Mapped[int] = mapped_column(ForeignKey("participants.id"))

    participant: Mapped["Participant"] = relationship(lazy="joined")

    def __str__(self):
        return f"Vote: {self.tg_id} {self.participant_id} {self.nomination_id}"


class Settings(Requests, Base):
    __tablename__ = "settings"

    voting_enabled: Mapped[bool] = mapped_column(primary_key=True)
