from fanfan.core.exceptions.base import AppException


class UsersException(AppException):
    pass


class UserNotFound(UsersException):
    user_message = "Пользователь не найден"
