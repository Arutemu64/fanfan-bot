from dishka import Provider, Scope, provide

from fanfan.application.common.announcer import Announcer
from fanfan.application.common.notifier import Notifier


class UtilsProvider(Provider):
    notifier = provide(Notifier, scope=Scope.REQUEST)
    announcer = provide(Announcer, scope=Scope.REQUEST)
