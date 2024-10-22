from fanfan.core.exceptions.base import AppException


class Cosplay2Exceptions(AppException):
    pass


class NoCosplay2ConfigProvided(Cosplay2Exceptions):
    message = "⚠️ Не предоставлены настройки Cosplay2"
