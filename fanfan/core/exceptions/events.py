import time

from fanfan.core.exceptions.base import AppException
from fanfan.core.utils.pluralize import SECONDS_PLURALS, pluralize


class EventsException(AppException):
    pass


class EventNotFound(EventsException):
    message = "⚠️ Выступление не найдено"

    def __init__(self, event_id: int | None = None) -> None:
        if isinstance(event_id, int):
            self.message = f"⚠️ Выступление под номером {event_id} не найдено"


class NoCurrentEvent(EventNotFound):
    message = "⚠️ Текущее выступление не найдено"


class NoNextEvent(EventNotFound):
    message = "👏 Выступления закончились, спасибо за работу! Увидимся! 😉"


class AnnounceTooFast(EventsException):
    def __init__(self, announcement_timeout: int, old_timestamp: float) -> None:
        time_left = int(old_timestamp + announcement_timeout - time.time())
        self.message = (
            f"⚠️ С последнего анонса не прошло {announcement_timeout} "
            f"{pluralize(announcement_timeout, SECONDS_PLURALS)}!\n"
            f"Попробуйте ещё раз через "
            f"{time_left} {pluralize(time_left, SECONDS_PLURALS)}."
        )


class CurrentEventNotAllowed(EventsException):
    message = "⚠️ Это выступление является текущим"


class SkippedEventNotAllowed(EventsException):
    message = "⚠️ Это выступление пропущено"


class SameEventsAreNotAllowed(EventsException):
    message = "⚠️ Выступления не могут совпадать"
