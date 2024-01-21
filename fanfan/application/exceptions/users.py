from fanfan.application.exceptions import ServiceError


class UserServiceError(ServiceError):
    message = "⚠️ Произошла неизвестная ошибка в сервисе пользователей"


class UserServiceNotFound(UserServiceError):
    message = "⚠️ Пользователь не найден"


class UserServiceHasNoTicket(UserServiceError):
    message = "⚠️ У пользователя не привязан билет"
