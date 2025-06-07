from fanfan.core.exceptions.base import AppException


class TicketsException(AppException):
    pass


class TicketNotFound(TicketsException):
    default_message = "Билет не найден"


class UserAlreadyHasTicketLinked(TicketsException):
    default_message = "Билет уже привязан"


class TicketAlreadyUsed(TicketsException):
    default_message = "Этот билет уже использован"


class TicketNotLinked(TicketsException):
    default_message = "Привяжите билет для доступа к этой функции"
