from fanfan.core.exceptions.base import AppException


class SettingsException(AppException):
    message = "⚠️ Неизвестная ошибка в сервисе настроек"


class SettingsNotFound(SettingsException):
    pass
