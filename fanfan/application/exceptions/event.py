from typing import Optional

from fanfan.application.exceptions import ServiceError
from fanfan.common.utils import SECONDS_PLURALS, pluralize


class EventServiceError(ServiceError):
    message = "⚠️ Произошла неизвестная ошибка в сервисе событий"


class EventNotFound(EventServiceError):
    message = "⚠️ Выступление не найдено"

    def __init__(self, event_id: Optional[int] = None):
        if isinstance(event_id, int):
            self.message = f"⚠️ Выступление под номером {event_id} не найдено"


class NoCurrentEvent(EventNotFound):
    message = "⚠️ Текущее выступление не найдено"


class NoNextEvent(EventNotFound):
    message = "👏 Выступления закончились, спасибо за работу! Увидимся через год! 😉"


class AnnounceTooFast(EventServiceError):
    def __init__(self, announcement_timeout: int, time_left: int) -> None:
        self.message = (
            f"⚠️ С последнего анонса не прошло {announcement_timeout} "
            f"{pluralize(announcement_timeout, SECONDS_PLURALS)}!\n"
            f"Попробуйте ещё раз через "
            f"{time_left} {pluralize(time_left, SECONDS_PLURALS)}."
        )


class CurrentEventNotAllowed(EventServiceError):
    message = "⚠️ Это выступление является текущим"


class SkippedEventNotAllowed(EventServiceError):
    message = "⚠️ Это выступление пропущено"


class SameEventsAreNotAllowed(EventServiceError):
    message = "⚠️ Выступления не могут совпадать"
