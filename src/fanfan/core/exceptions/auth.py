from fanfan.core.exceptions.base import AppException


class AuthenticationError(AppException):
    user_message = "Ошибка авторизации"


class NoUserContextError(AuthenticationError):
    pass
