from fanfan.core.exceptions.base import AppException


class AuthenticationError(AppException):
    message = "⚠️ Ошибка авторизации"


class NoUserContextError(AuthenticationError):
    pass
