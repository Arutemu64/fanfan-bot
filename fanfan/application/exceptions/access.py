from fanfan.application.exceptions import ServiceError


class AccessDenied(ServiceError):
    message = "⚠️ У вас нет доступа к этой функции"


class TicketNotLinked(AccessDenied):
    message = "⚠️🎫 Привяжите билет для доступа к этой функции"


class NoIdentityProvided(AccessDenied):
    pass
