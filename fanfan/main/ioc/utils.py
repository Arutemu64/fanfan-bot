from dishka import Provider, Scope, provide

from fanfan.adapters.utils.limit import LimitFactory
from fanfan.adapters.utils.notifier import BotNotifier
from fanfan.adapters.utils.task_manager import TaskManager


class UtilsProvider(Provider):
    limiter = provide(LimitFactory, scope=Scope.APP)
    notifier = provide(BotNotifier, scope=Scope.APP)
    task_manager = provide(TaskManager, scope=Scope.REQUEST)
