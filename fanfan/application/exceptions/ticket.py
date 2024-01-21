from fanfan.application.exceptions import ServiceError


class TicketServiceError(ServiceError):
    message = "⚠️ Произошла неизвестная ошибка в сервисе билетов"


class TicketNotFound(TicketServiceError):
    message = "⚠️ Билет не найден"


class UserHasNoTicketLinked(TicketServiceError):
    user_message = "⚠️ Билет не привязан"


class UserAlreadyHasTicketLinked(TicketServiceError):
    user_message = "⚠️ Билет уже привязан"


class TicketAlreadyUsed(TicketServiceError):
    user_message = "⚠️ Этот билет уже использован"


class TicketAlreadyExist(TicketServiceError):
    user_message = "⚠️ Билет с таким номером уже существует"
