from fanfan.core.exceptions.base import AppException


class TicketsException(AppException):
    pass


class TicketNotFound(TicketsException):
    user_message = "Билет не найден"


class UserAlreadyHasTicketLinked(TicketsException):
    user_message = "Билет уже привязан"


class TicketAlreadyUsed(TicketsException):
    user_message = "Этот билет уже использован"


class TicketNotLinked(TicketsException):
    user_message = "Привяжите билет для доступа к этой функции"
