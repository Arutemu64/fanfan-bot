from fanfan.core.exceptions.base import AppException


class CodesException(AppException):
    pass


class CodeNotFound(CodesException):
    message = "⚠️ Неизвестный QR-код"
