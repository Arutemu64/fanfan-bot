from dishka import Provider, Scope, provide

from fanfan.core.services.access import UserAccessValidator
from fanfan.core.services.tickets import TicketsService


class ServicesProvider(Provider):
    scope = Scope.REQUEST

    access = provide(UserAccessValidator)
    tickets = provide(TicketsService)
