from dishka import Provider, Scope, provide

from fanfan.application.common.limiter import Limiter
from fanfan.application.common.notifier import Notifier
from fanfan.application.common.task_manager import TaskManager


class UtilsProvider(Provider):
    limiter = provide(Limiter, scope=Scope.APP)
    notifier = provide(Notifier, scope=Scope.REQUEST)
    task_manager = provide(TaskManager, scope=Scope.REQUEST)
