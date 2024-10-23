from dishka import Provider, Scope, provide

from fanfan.adapters.utils.limiter import Limiter
from fanfan.adapters.utils.notifier import Notifier
from fanfan.adapters.utils.task_manager import TaskManager


class UtilsProvider(Provider):
    limiter = provide(Limiter, scope=Scope.APP)
    notifier = provide(Notifier, scope=Scope.APP)
    task_manager = provide(TaskManager, scope=Scope.REQUEST)
