from fanfan.core.exceptions.base import AppException


class AuthenticationError(AppException):
    default_message = "Ошибка авторизации"


class NoUserContextError(AuthenticationError):
    pass
