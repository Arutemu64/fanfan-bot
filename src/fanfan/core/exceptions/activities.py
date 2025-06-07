from fanfan.core.exceptions.base import AppException


class ActivitiesException(AppException):
    pass


class ActivityNotFound(ActivitiesException):
    default_message = "Активность не найдена"
