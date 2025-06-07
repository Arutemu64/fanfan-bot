import time

from fanfan.core.exceptions.base import AppException
from fanfan.core.utils.pluralize import SECONDS_PLURALS, pluralize


class ScheduleException(AppException):
    pass


class EventNotFound(ScheduleException):
    user_message = "Выступление не найдено"

    def __init__(self, event_id: int | None = None) -> None:
        if isinstance(event_id, int):
            self.message = f"Выступление под номером {event_id} не найдено"


class NoNextEvent(EventNotFound):
    user_message = "Выступления закончились, спасибо за работу!"


class ScheduleEditTooFast(ScheduleException):
    def __init__(self, announcement_timeout: float, old_timestamp: float) -> None:
        time_left = int(old_timestamp + announcement_timeout - time.time())
        self.message = (
            f"С последнего изменения расписания "
            f"не прошло {int(announcement_timeout)} "
            f"{pluralize(int(announcement_timeout), SECONDS_PLURALS)}!\n"
            f"Попробуйте ещё раз через "
            f"{time_left} {pluralize(time_left, SECONDS_PLURALS)}."
        )


class CurrentEventNotAllowed(ScheduleException):
    user_message = "Это выступление является текущим"


class SameEventsAreNotAllowed(ScheduleException):
    user_message = "Выступления не могут совпадать"


class ScheduleChangeNotFound(ScheduleException):
    user_message = "Изменение расписания не найдено. Возможно, оно отменено."


class OutdatedScheduleChange(ScheduleException):
    user_message = "Это изменение уже неактуально."
