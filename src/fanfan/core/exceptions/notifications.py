from fanfan.core.exceptions.base import AppException


class NotificationsException(AppException):
    pass


class MailingNotFound(NotificationsException):
    default_message = "Рассылка не найдена"
