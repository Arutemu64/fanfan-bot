from dishka import Provider, Scope, provide

from fanfan.adapters.utils.notifier import BotNotifier
from fanfan.adapters.utils.rate_lock import RateLockFactory


class UtilsProvider(Provider):
    rate_limit_factory = provide(RateLockFactory, scope=Scope.APP)
    notifier = provide(BotNotifier, scope=Scope.APP)
