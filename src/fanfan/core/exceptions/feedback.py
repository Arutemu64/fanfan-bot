from fanfan.core.exceptions.base import AppException


class FeedbackException(AppException):
    pass


class FeedbackNotFound(FeedbackException):
    default_message = "Обратная связь не найдена"


class FeedbackAlreadyProcessed(FeedbackException):
    default_message = "Обратная связь уже обработана"
