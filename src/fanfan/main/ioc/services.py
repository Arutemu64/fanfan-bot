from dishka import Provider, Scope, provide

from fanfan.core.services.access import UserAccessValidator


class ServicesProvider(Provider):
    scope = Scope.REQUEST

    access = provide(UserAccessValidator)
