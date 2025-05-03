import time

from fanfan.core.exceptions.base import AppException


class LimiterException(AppException):
    message = "⚠️ Неизвестная ошибка при запуске задачи"


class RateLimitCooldown(LimiterException):
    def __init__(self, cooldown_period: float, timestamp: float):
        self.limit_timeout = cooldown_period
        self.current_timestamp = timestamp
        time_left = int(timestamp + cooldown_period - time.time())
        self.message = (
            f"⚠️ Задача выполняется слишком часто.Попробуйте через {time_left} с."
        )


class RateLimiterInUse(LimiterException):
    message = "⚠️ Задача уже выполняется"
