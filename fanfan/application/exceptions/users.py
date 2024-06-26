from fanfan.application.exceptions import ServiceError


class UserServiceError(ServiceError):
    message = "⚠️ Произошла неизвестная ошибка в сервисе пользователей"


class UserNotFound(UserServiceError):
    message = "⚠️ Пользователь не найден"


class UserAlreadyExist(UserServiceError):
    message = "⚠️ Пользователь уже существует"


class UserHasNoTicket(UserServiceError):
    message = "⚠️ У пользователя не привязан билет"
