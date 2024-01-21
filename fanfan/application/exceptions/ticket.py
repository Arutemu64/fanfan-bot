from fanfan.application.exceptions import ServiceError


class TicketServiceError(ServiceError):
    message = "⚠️ Произошла неизвестная ошибка в сервисе билетов"


class TicketNotFound(TicketServiceError):
    message = "⚠️ Билет не найден"


class UserHasNoTicketLinked(TicketServiceError):
    message = "⚠️ У участника не привязан билет"


class UserAlreadyHasTicketLinked(TicketServiceError):
    message = "⚠️ Билет уже привязан"


class TicketAlreadyUsed(TicketServiceError):
    message = "⚠️ Этот билет уже использован"


class TicketAlreadyExist(TicketServiceError):
    message = "⚠️ Билет с таким номером уже существует"
