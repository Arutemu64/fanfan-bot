import time

from fanfan.core.exceptions.access import AccessDenied
from fanfan.core.exceptions.base import AppException
from fanfan.core.utils.pluralize import SECONDS_PLURALS, pluralize


class ScheduleException(AppException):
    pass


class EventNotFound(ScheduleException):
    message = "⚠️ Выступление не найдено"

    def __init__(self, event_id: int | None = None) -> None:
        if isinstance(event_id, int):
            self.message = f"⚠️ Выступление под номером {event_id} не найдено"


class NoCurrentEvent(EventNotFound):
    message = "⚠️ Текущее выступление не найдено"


class NoNextEvent(EventNotFound):
    message = "👏 Выступления закончились, спасибо за работу! Увидимся! 😉"


class ScheduleEditTooFast(ScheduleException):
    def __init__(self, announcement_timeout: float, old_timestamp: float) -> None:
        time_left = int(old_timestamp + announcement_timeout - time.time())
        self.message = (
            f"⚠️ С последнего изменения расписания "
            f"не прошло {int(announcement_timeout)} "
            f"{pluralize(int(announcement_timeout), SECONDS_PLURALS)}!\n"
            f"Попробуйте ещё раз через "
            f"{time_left} {pluralize(time_left, SECONDS_PLURALS)}."
        )


class CurrentEventNotAllowed(ScheduleException):
    message = "⚠️ Это выступление является текущим"


class SkippedEventNotAllowed(ScheduleException):
    message = "⚠️ Это выступление пропущено"


class SameEventsAreNotAllowed(ScheduleException):
    message = "⚠️ Выступления не могут совпадать"


class ScheduleChangeNotFound(ScheduleException):
    message = "⚠️ Изменение расписания не найдено. Возможно, оно отменено."


class OutdatedScheduleChange(ScheduleException):
    message = "⚠️ Это изменение уже неактуально."


class NoScheduleEditingPermission(ScheduleException, AccessDenied):
    message = "⚠️ У вас нет прав для редактирования расписания"
