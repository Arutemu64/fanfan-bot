from fanfan.core.exceptions.base import AppException


class QRValidationError(AppException):
    message = "⚠️ Ошибка при валидации QR-кода"
