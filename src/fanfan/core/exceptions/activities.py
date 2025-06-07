from fanfan.core.exceptions.base import AppException


class ActivitiesException(AppException):
    pass


class ActivityNotFound(ActivitiesException):
    user_message = "Активность не найдена"
