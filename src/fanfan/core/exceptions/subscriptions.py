from fanfan.core.exceptions.base import AppException


class SubscriptionsException(AppException):
    pass


class SubscriptionAlreadyExist(SubscriptionsException):
    default_message = "Вы уже подписаны на это выступление"


class SubscriptionNotFound(SubscriptionsException):
    default_message = "Подписка не найдена"
