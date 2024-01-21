from fanfan.application.exceptions import ServiceError


class SettingsServiceError(ServiceError):
    message = "⚠️ Неизвестная ошибка в сервисе настроек"


class SettingsServiceNotFound(SettingsServiceError):
    pass
