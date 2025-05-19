from fanfan.core.exceptions.base import AppException


class MailingException(AppException):
    pass


class MailingNotFound(MailingException):
    message = "⚠️ Рассылка не найдена"
