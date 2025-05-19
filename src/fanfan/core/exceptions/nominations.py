from fanfan.core.exceptions.base import AppException


class NominationsException(AppException):
    pass


class NominationNotFound(NominationsException):
    message = "⚠️ Номинация не найдена"
