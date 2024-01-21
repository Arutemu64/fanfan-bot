import sentry_sdk
from sqlalchemy.ext.asyncio import AsyncSession

from .repositories import (
    AchievementsRepository,
    # AchievementsRepository,
    # EventsRepository,
    NominationsRepository,
    ParticipantsRepository,
    SettingsRepository,
    SubscriptionsRepository,
    # SubscriptionsRepository,
    TicketsRepository,
    # TransactionsRepository,
    UsersRepository,
    VotesRepository,
)
from .repositories.events import EventsRepository


class UnitOfWork:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.achievements = AchievementsRepository(self.session)
        self.events = EventsRepository(self.session)
        self.nominations = NominationsRepository(self.session)
        self.participants = ParticipantsRepository(self.session)
        self.settings = SettingsRepository(self.session)
        self.subscriptions = SubscriptionsRepository(self.session)
        self.tickets = TicketsRepository(self.session)
        self.users = UsersRepository(self.session)
        self.votes = VotesRepository(self.session)

    async def __aenter__(self):
        self.nested = await self.session.begin_nested()
        self.sentry_transaction = sentry_sdk.start_transaction(name="UOWTransaction")

    async def __aexit__(self, *args):
        if self.nested.is_active:
            await self.nested.rollback()
        self.sentry_transaction.finish()

    async def rollback(self):
        await self.nested.rollback()

    async def commit(self):
        await self.session.commit()
