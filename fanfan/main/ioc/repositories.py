from dishka import Provider, Scope, provide

from fanfan.adapters.db.repositories.achievements import (
    AchievementsRepository,
)
from fanfan.adapters.db.repositories.activities import ActivitiesRepository
from fanfan.adapters.db.repositories.codes import CodesRepository
from fanfan.adapters.db.repositories.feedback import FeedbackRepository
from fanfan.adapters.db.repositories.flags import FlagsRepository
from fanfan.adapters.db.repositories.markets import MarketsRepository
from fanfan.adapters.db.repositories.nominations import NominationsRepository
from fanfan.adapters.db.repositories.participants import (
    ParticipantsRepository,
)
from fanfan.adapters.db.repositories.products import ProductsRepository
from fanfan.adapters.db.repositories.quest import QuestRepository
from fanfan.adapters.db.repositories.schedule_blocks import ScheduleBlocksRepository
from fanfan.adapters.db.repositories.schedule_changes import ScheduleChangesRepository
from fanfan.adapters.db.repositories.schedule_events import ScheduleEventsRepository
from fanfan.adapters.db.repositories.settings import (
    SettingsRepository,
)
from fanfan.adapters.db.repositories.subscriptions import (
    SubscriptionsRepository,
)
from fanfan.adapters.db.repositories.tickets import TicketsWriter
from fanfan.adapters.db.repositories.transactions import TransactionsRepository
from fanfan.adapters.db.repositories.users import UsersRepository
from fanfan.adapters.db.repositories.votes import VotesRepository
from fanfan.adapters.redis.dao.mailing import MailingDAO


class RepositoriesProvider(Provider):
    scope = Scope.REQUEST

    # RDB

    achievements = provide(AchievementsRepository)
    activities = provide(ActivitiesRepository)
    codes = provide(CodesRepository)
    feedback = provide(FeedbackRepository)
    markets = provide(MarketsRepository)
    nominations = provide(NominationsRepository)
    participants = provide(ParticipantsRepository)
    products = provide(ProductsRepository)
    quest = provide(QuestRepository)
    schedule_events = provide(ScheduleEventsRepository)
    schedule_blocks = provide(ScheduleBlocksRepository)
    schedule_changes = provide(ScheduleChangesRepository)
    settings = provide(SettingsRepository)
    subscriptions = provide(SubscriptionsRepository)
    tickets = provide(TicketsWriter)
    users = provide(UsersRepository)
    votes = provide(VotesRepository)
    transactions = provide(TransactionsRepository)
    flags = provide(FlagsRepository)

    # Redis
    mailing = provide(MailingDAO)
