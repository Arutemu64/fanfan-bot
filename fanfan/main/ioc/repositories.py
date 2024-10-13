from dishka import Provider, Scope, provide

from fanfan.infrastructure.db.repositories.achievements import (
    AchievementsRepository,
)
from fanfan.infrastructure.db.repositories.activities import ActivitiesRepository
from fanfan.infrastructure.db.repositories.events import EventsRepository
from fanfan.infrastructure.db.repositories.feedback import FeedbackRepository
from fanfan.infrastructure.db.repositories.nominations import NominationsRepository
from fanfan.infrastructure.db.repositories.participants import (
    ParticipantsRepository,
)
from fanfan.infrastructure.db.repositories.quest import QuestRepository
from fanfan.infrastructure.db.repositories.settings import (
    SettingsRepository,
)
from fanfan.infrastructure.db.repositories.subscriptions import (
    SubscriptionsRepository,
)
from fanfan.infrastructure.db.repositories.tickets import TicketsRepository
from fanfan.infrastructure.db.repositories.users import UsersRepository
from fanfan.infrastructure.db.repositories.votes import VotesRepository
from fanfan.infrastructure.redis.repositories.mailing import MailingRepository


class RepositoriesProvider(Provider):
    scope = Scope.REQUEST

    # RDB
    achievements = provide(AchievementsRepository)
    activities = provide(ActivitiesRepository)
    events = provide(EventsRepository)
    feedback = provide(FeedbackRepository)
    nominations = provide(NominationsRepository)
    participants = provide(ParticipantsRepository)
    quest = provide(QuestRepository)
    settings = provide(SettingsRepository)
    subscriptions = provide(SubscriptionsRepository)
    tickets = provide(TicketsRepository)
    users = provide(UsersRepository)
    votes = provide(VotesRepository)

    # Redis
    mailing = provide(MailingRepository)
