from fanfan.core.exceptions.base import AppException


class FeedbackException(AppException):
    pass


class FeedbackNotFound(FeedbackException):
    user_message = "Обратная связь не найдена"


class FeedbackAlreadyProcessed(FeedbackException):
    user_message = "Обратная связь уже обработана"
