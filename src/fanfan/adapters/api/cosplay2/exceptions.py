from fanfan.core.exceptions.base import AppException


class Cosplay2Exception(AppException):
    pass


class NoCosplay2ConfigProvided(Cosplay2Exception):
    default_message = "⚠️ Не предоставлены настройки Cosplay2"
