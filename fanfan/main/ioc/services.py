from dishka import Provider, Scope, provide

from fanfan.core.services.access import AccessService


class ServicesProvider(Provider):
    scope = Scope.REQUEST

    access = provide(AccessService)
