from dishka import Provider, Scope, provide

from fanfan.core.services.mailing import MailingService
from fanfan.core.services.market import MarketService
from fanfan.core.services.permissions import UserPermissionService
from fanfan.core.services.quest import QuestService
from fanfan.core.services.schedule import ScheduleService
from fanfan.core.services.tickets import TicketsService
from fanfan.core.services.ticketscloud import TCloudService
from fanfan.core.services.voting import VotingService


class ServicesProvider(Provider):
    scope = Scope.REQUEST

    mailing = provide(MailingService)
    market = provide(MarketService)
    quest = provide(QuestService)
    schedule = provide(ScheduleService)
    tickets = provide(TicketsService)
    voting = provide(VotingService)
    user_perms = provide(UserPermissionService)
    tcloud = provide(TCloudService)
