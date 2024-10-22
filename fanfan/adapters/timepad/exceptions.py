from fanfan.core.exceptions.base import AppException


class TimepadException(AppException):
    pass


class NoTimepadConfigProvided(TimepadException):
    message = "⚠️ Не предоставлены настройки TimePad"
