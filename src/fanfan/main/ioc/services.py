from dishka import Provider, Scope, provide

from fanfan.core.services.feedback import FeedbackService
from fanfan.core.services.mailing import MailingService
from fanfan.core.services.market import MarketService
from fanfan.core.services.quest import QuestService
from fanfan.core.services.schedule import ScheduleService
from fanfan.core.services.tickets import TicketsService
from fanfan.core.services.user import UserService
from fanfan.core.services.voting import VotingService


class ServicesProvider(Provider):
    scope = Scope.REQUEST

    feedback = provide(FeedbackService)
    mailing = provide(MailingService)
    market = provide(MarketService)
    quest = provide(QuestService)
    schedule = provide(ScheduleService)
    tickets = provide(TicketsService)
    user = provide(UserService)
    voting = provide(VotingService)
