from fanfan.core.exceptions.base import AppException


class TaskException(AppException):
    message = "⚠️ Неизвестная ошибка при запуске задачи"


class TooFast(TaskException):
    message = "⚠️ Задача выполняется слишком часто"


class TaskInProgress(TaskException):
    message = "⚠️ Задача уже выполняется"


class NoTimepadConfigProvided(TaskException):
    message = "⚠️ Не предоставлены настройки TimePad"
