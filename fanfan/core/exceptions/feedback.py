from fanfan.core.exceptions.base import AppException


class FeedbackException(AppException):
    pass


class FeedbackNotFound(FeedbackException):
    message = "⚠️ Обратная связь не найдена"


class FeedbackAlreadyProcessed(FeedbackException):
    message = "⚠️ Обратная связь уже обработана"
