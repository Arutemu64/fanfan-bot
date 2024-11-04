from fanfan.core.exceptions.access import AccessDenied
from fanfan.core.exceptions.base import AppException


class UsersException(AppException):
    pass


class UserNotFound(UsersException):
    message = "⚠️ Пользователь не найден"


class UserAlreadyExist(UsersException):
    message = "⚠️ Пользователь уже существует"


class TicketNotLinked(AccessDenied):
    message = "⚠️ Привяжите билет для доступа к этой функции"


class OrgSettingsNotFound(UsersException):
    pass
