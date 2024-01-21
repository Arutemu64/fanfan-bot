from typing import Optional

from fanfan.application.exceptions import ServiceError


class EventServiceError(ServiceError):
    message = "⚠️ Произошла неизвестная ошибка в сервисе событий"


class EventNotFound(EventServiceError):
    message = "⚠️ Выступление не найдено"

    def __init__(self, event_id: Optional[int] = None):
        if event_id:
            self.message = f"⚠️ Выступление под номером {event_id} не найдено"


class NoCurrentEvent(EventNotFound):
    message = "⚠️ Текущее выступление не найдено"


class NoNextEvent(EventNotFound):
    message = "👏 Выступления закончились, спасибо за работу! Увидимся через год! 😉"


class AnnounceTooFast(EventServiceError):
    @staticmethod
    def _seconds_pluralize(seconds: int) -> str:
        if (seconds % 10 == 1) and (seconds % 100 != 11):
            return "секунду"
        elif (2 <= seconds % 10 <= 4) and (seconds % 100 < 10 or seconds % 100 >= 20):
            return "секунды"
        else:
            return "секунд"

    def __init__(self, announcement_timeout: int, time_left: int) -> None:
        self.message = (
            f"⚠️ С последнего анонса не прошло {announcement_timeout} "
            f"{self._seconds_pluralize(announcement_timeout)}! "
            f"Попробуйте ещё раз через {time_left} {self._seconds_pluralize(time_left)}."
        )


class CurrentEventNotAllowed(EventServiceError):
    message = "⚠️ Это выступление является текущим"


class SkippedEventNotAllowed(EventServiceError):
    message = "⚠️ Это выступление пропущено"


class SameEventsAreNotAllowed(EventServiceError):
    message = "⚠️ Выступления не могут совпадать"
