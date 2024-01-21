from fanfan.application.exceptions import ServiceError


class SubscriptionsError(ServiceError):
    message = "⚠️ Произошла неизвестная ошибка в сервисе подписок"


class SubscriptionAlreadyExist(ServiceError):
    message = "⚠️ Вы уже подписаны на это выступление"


class SubscriptionNotFound(ServiceError):
    message = "⚠️ Подписка не найдена"
