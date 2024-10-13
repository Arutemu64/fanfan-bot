from fanfan.core.exceptions.base import AppException


class QuestException(AppException):
    pass


class QuestRegistrationClosed(QuestException):
    message = "⚠️ Регистрация на квест закрыта"


class AlreadyRegistered(QuestException):
    message = "⚠️ Пользователь уже зарегистрирован на квест"
