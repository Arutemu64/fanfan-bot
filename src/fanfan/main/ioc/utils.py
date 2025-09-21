from dishka import Provider, Scope, provide

from fanfan.adapters.utils.notifier import TgBotNotifier
from fanfan.adapters.utils.rate_lock import RateLockFactory


class UtilsProvider(Provider):
    rate_limit_factory = provide(RateLockFactory, scope=Scope.APP)
    notifier = provide(TgBotNotifier, scope=Scope.APP)
