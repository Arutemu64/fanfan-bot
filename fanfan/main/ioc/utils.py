from dishka import Provider, Scope, provide

from fanfan.adapters.utils.notifier import BotNotifier
from fanfan.adapters.utils.rate_limit import RateLimitFactory


class UtilsProvider(Provider):
    rate_limit_factory = provide(RateLimitFactory, scope=Scope.APP)
    notifier = provide(BotNotifier, scope=Scope.APP)
