from fanfan.core.exceptions.base import AppException


class CodesException(AppException):
    pass


class CodeNotFound(CodesException):
    default_message = "Неизвестный QR-код"
