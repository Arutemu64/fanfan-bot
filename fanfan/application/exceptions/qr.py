from fanfan.application.exceptions import ServiceError


class QRNotFound(ServiceError):
    message = "⚠️ Неверный QR-код"
