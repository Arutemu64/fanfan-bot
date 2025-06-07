from fanfan.core.exceptions.base import AppException


class TCloudException(AppException):
    pass


class NoTCloudConfigProvided(TCloudException):
    default_message = "⚠️ Не предоставлены настройки TimePad"
