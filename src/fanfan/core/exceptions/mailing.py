from fanfan.core.exceptions.base import AppException


class MailingException(AppException):
    pass


class MailingNotFound(MailingException):
    default_message = "Рассылка не найдена"
