from typing import Union

from sqlalchemy import URL
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine as _create_async_engine
from sqlalchemy.orm import sessionmaker

from src.config import conf

from .repositories import (
    EventRepo,
    NominationRepo,
    ParticipantRepo,
    SubscriptionRepo,
    TicketRepo,
    UserRepo,
    VoteRepo,
)


def create_async_engine(url: Union[URL, str]) -> AsyncEngine:
    """
    :param url:
    :return:
    """
    return _create_async_engine(url=url, echo=conf.debug, pool_pre_ping=True)


def create_session_maker(engine: AsyncEngine = None) -> sessionmaker:
    """
    :param engine:
    :return:
    """
    return sessionmaker(
        engine or create_async_engine(conf.db.build_connection_str()),
        class_=AsyncSession,
        expire_on_commit=False,
    )


class Database:
    """
    Database class is the highest abstraction level of database and
    can be used in the handlers or any others bot-side functions
    """

    event: EventRepo
    nomination: NominationRepo
    participant: ParticipantRepo
    subscription: SubscriptionRepo
    ticket: TicketRepo
    user: UserRepo
    vote: VoteRepo

    session: AsyncSession

    def __init__(
        self,
        session: AsyncSession,
        event: EventRepo = None,
        nomination: NominationRepo = None,
        participant: ParticipantRepo = None,
        subscription: SubscriptionRepo = None,
        ticket: TicketRepo = None,
        user: UserRepo = None,
        vote: VoteRepo = None,
    ):
        self.session = session
        self.event = event or EventRepo(session=session)
        self.nomination = nomination or NominationRepo(session=session)
        self.participant = participant or ParticipantRepo(session=session)
        self.subscription = subscription or SubscriptionRepo(session=session)
        self.ticket = ticket or TicketRepo(session=session)
        self.user = user or UserRepo(session=session)
        self.vote = vote or VoteRepo(session=session)
