from fanfan.core.exceptions.base import AppException


class NominationsException(AppException):
    pass


class NominationNotFound(NominationsException):
    default_message = "Номинация не найдена"
