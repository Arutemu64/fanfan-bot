from fanfan.core.exceptions.base import AppException


class QRException(AppException):
    pass


class BadQRData(QRException):
    default_message = "Неверные данные QR кода"
