from dishka import Provider, Scope, provide

from fanfan.adapters.db.repositories.achievements import (
    AchievementsRepository,
)
from fanfan.adapters.db.repositories.activities import ActivitiesRepository
from fanfan.adapters.db.repositories.feedback import FeedbackRepository
from fanfan.adapters.db.repositories.nominations import NominationsRepository
from fanfan.adapters.db.repositories.participants import (
    ParticipantsRepository,
)
from fanfan.adapters.db.repositories.quest import QuestRepository
from fanfan.adapters.db.repositories.schedule import ScheduleRepository
from fanfan.adapters.db.repositories.settings import (
    SettingsRepository,
)
from fanfan.adapters.db.repositories.subscriptions import (
    SubscriptionsRepository,
)
from fanfan.adapters.db.repositories.tickets import TicketsRepository
from fanfan.adapters.db.repositories.transactions import TransactionsRepository
from fanfan.adapters.db.repositories.users import UsersRepository
from fanfan.adapters.db.repositories.votes import VotesRepository
from fanfan.adapters.redis.repositories.mailing import MailingRepository


class RepositoriesProvider(Provider):
    scope = Scope.REQUEST

    # RDB
    achievements = provide(AchievementsRepository)
    activities = provide(ActivitiesRepository)
    events = provide(ScheduleRepository)
    feedback = provide(FeedbackRepository)
    nominations = provide(NominationsRepository)
    participants = provide(ParticipantsRepository)
    quest = provide(QuestRepository)
    settings = provide(SettingsRepository)
    subscriptions = provide(SubscriptionsRepository)
    tickets = provide(TicketsRepository)
    users = provide(UsersRepository)
    votes = provide(VotesRepository)
    transactions = provide(TransactionsRepository)

    # Redis
    mailing = provide(MailingRepository)
