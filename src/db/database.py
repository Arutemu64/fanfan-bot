from typing import Union

from sqlalchemy import URL
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine as _create_async_engine

from src.config import conf

from .repositories import (
    AchievementRepo,
    EventRepo,
    NominationRepo,
    ParticipantRepo,
    SettingsRepo,
    SubscriptionRepo,
    TicketRepo,
    TransactionRepo,
    UserRepo,
    VoteRepo,
)


def create_async_engine(url: Union[URL, str]) -> AsyncEngine:
    return _create_async_engine(url=url, echo=conf.db_echo, pool_pre_ping=True)


def create_session_pool(engine: AsyncEngine = None) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        bind=engine or create_async_engine(conf.db.build_connection_str()),
        class_=AsyncSession,
        expire_on_commit=False,
    )


class Database:
    """
    Database class is the highest abstraction level of database and
    can be used in the handlers or any others bot-side functions
    """

    session: AsyncSession

    event: EventRepo
    achievement: AchievementRepo
    nomination: NominationRepo
    participant: ParticipantRepo
    settings: SettingsRepo
    subscription: SubscriptionRepo
    ticket: TicketRepo
    transaction: TransactionRepo
    user: UserRepo
    vote: VoteRepo

    def __init__(
        self,
        session: AsyncSession,
        achievement: AchievementRepo = None,
        event: EventRepo = None,
        nomination: NominationRepo = None,
        participant: ParticipantRepo = None,
        settings: SettingsRepo = None,
        subscription: SubscriptionRepo = None,
        ticket: TicketRepo = None,
        transaction: TransactionRepo = None,
        user: UserRepo = None,
        vote: VoteRepo = None,
    ):
        self.session = session
        self.achievement = achievement or AchievementRepo(session=session)
        self.event = event or EventRepo(session=session)
        self.nomination = nomination or NominationRepo(session=session)
        self.participant = participant or ParticipantRepo(session=session)
        self.settings = settings or SettingsRepo(session=session)
        self.subscription = subscription or SubscriptionRepo(session=session)
        self.ticket = ticket or TicketRepo(session=session)
        self.transaction = transaction or TransactionRepo(session=session)
        self.user = user or UserRepo(session=session)
        self.vote = vote or VoteRepo(session=session)
