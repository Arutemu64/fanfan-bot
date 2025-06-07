from fanfan.core.exceptions.base import AppException


class SubscriptionsException(AppException):
    pass


class SubscriptionAlreadyExist(SubscriptionsException):
    user_message = "Вы уже подписаны на это выступление"


class SubscriptionNotFound(SubscriptionsException):
    user_message = "Подписка не найдена"
