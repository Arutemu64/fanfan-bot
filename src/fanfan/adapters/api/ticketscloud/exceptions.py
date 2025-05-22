from fanfan.core.exceptions.base import AppException


class TCloudException(AppException):
    pass


class NoTCloudConfigProvided(TCloudException):
    message = "⚠️ Не предоставлены настройки TimePad"


class TCloudOrderProcessFailed(TCloudException):
    pass
