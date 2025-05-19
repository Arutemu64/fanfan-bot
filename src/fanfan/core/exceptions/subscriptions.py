from fanfan.core.exceptions.base import AppException


class SubscriptionsException(AppException):
    message = "⚠️ Произошла неизвестная ошибка в сервисе подписок"


class SubscriptionAlreadyExist(SubscriptionsException):
    message = "⚠️ Вы уже подписаны на это выступление"


class SubscriptionNotFound(SubscriptionsException):
    message = "⚠️ Подписка не найдена"
