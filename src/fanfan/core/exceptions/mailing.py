from fanfan.core.exceptions.base import AppException


class MailingException(AppException):
    pass


class MailingNotFound(MailingException):
    user_message = "Рассылка не найдена"
