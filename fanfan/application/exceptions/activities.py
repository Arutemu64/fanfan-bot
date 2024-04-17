from fanfan.application.exceptions import ServiceError


class ActivitiesServiceError(ServiceError):
    message = "⚠️ Произошла неизвестная ошибка в сервисе событий"


class ActivityNotFound(ActivitiesServiceError):
    message = "⚠️ Активность не найдена"
