from fanfan.core.exceptions.access import AccessDenied
from fanfan.core.exceptions.base import AppException


class FeedbackException(AppException):
    pass


class FeedbackNotFound(FeedbackException):
    message = "⚠️ Обратная связь не найдена"


class FeedbackAlreadyProcessed(FeedbackException):
    message = "⚠️ Обратная связь уже обработана"


class NoFeedbackPermission(FeedbackException, AccessDenied):
    message = "⚠️ У вас нет прав для отправки обратной связи"
