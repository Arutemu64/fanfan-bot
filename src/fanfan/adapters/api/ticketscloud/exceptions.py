from fanfan.core.exceptions.base import AppException


class TCloudException(AppException):
    pass


class NoTCloudConfigProvided(TCloudException):
    user_message = "⚠️ Не предоставлены настройки TimePad"
