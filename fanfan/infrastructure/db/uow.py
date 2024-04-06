from sqlalchemy.ext.asyncio import AsyncSession

from .repositories import (
    AchievementsRepository,
    ActivitiesRepository,
    EventsRepository,
    NominationsRepository,
    ParticipantsRepository,
    QuotesRepository,
    SettingsRepository,
    SubscriptionsRepository,
    TicketsRepository,
    UsersRepository,
    VotesRepository,
)


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
        self.activities = ActivitiesRepository(self.session)
        self.quotes = QuotesRepository(self.session)

    async def __aenter__(self):
        pass

    async def __aexit__(self, *args):
        await self.session.rollback()
        await self.session.close()

    async def rollback(self):
        await self.session.rollback()

    async def commit(self):
        await self.session.commit()
