from fanfan.core.exceptions.base import AppException


class TicketsException(AppException):
    message = "⚠️ Произошла неизвестная ошибка в сервисе билетов"


class TicketNotFound(TicketsException):
    message = "⚠️ Билет не найден"


class UserAlreadyHasTicketLinked(TicketsException):
    message = "⚠️ Билет уже привязан"


class TicketAlreadyUsed(TicketsException):
    message = "⚠️ Этот билет уже использован"


class TicketAlreadyExist(TicketsException):
    message = "⚠️ Билет с таким номером уже существует"
