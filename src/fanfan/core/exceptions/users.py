from fanfan.core.exceptions.access import AccessDenied
from fanfan.core.exceptions.base import AppException
from fanfan.core.exceptions.tickets import TicketsException


class UsersException(AppException):
    pass


class UserNotFound(UsersException):
    message = "⚠️ Пользователь не найден"


class NoUserManagerPermission(TicketsException, AccessDenied):
    message = "⚠️ Вы не можете просматривать информацию о других пользователях"
