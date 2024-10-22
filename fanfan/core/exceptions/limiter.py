import time

from fanfan.core.exceptions.base import AppException


class LimiterException(AppException):
    message = "⚠️ Неизвестная ошибка при запуске задачи"


class TooFast(LimiterException):
    def __init__(self, limit_timeout: float, current_timestamp: float):
        self.limit_timeout = limit_timeout
        self.current_timestamp = current_timestamp
        time_left = int(current_timestamp + limit_timeout - time.time())
        self.message = (
            f"⚠️ Задача выполняется слишком часто." f"Попробуйте через {time_left} с."
        )


class LimitLocked(LimiterException):
    message = "⚠️ Задача уже выполняется"
