from dishka import Provider, Scope, provide

from fanfan.application.common.announcer import Announcer
from fanfan.application.common.notifier import Notifier
from fanfan.application.common.task_manager import TaskManager


class UtilsProvider(Provider):
    notifier = provide(Notifier, scope=Scope.REQUEST)
    announcer = provide(Announcer, scope=Scope.REQUEST)
    task_manager = provide(TaskManager, scope=Scope.REQUEST)
