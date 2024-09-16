from fanfan.core.exceptions.base import AppException


class ActivitiesException(AppException):
    pass


class ActivityNotFound(ActivitiesException):
    message = "⚠️ Активность не найдена"
