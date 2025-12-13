import enum
from dataclasses import dataclass

from fanfan.core.vo.participant import ValueType


class RequestStatus(enum.StrEnum):
    PENDING = "pending"  # Проверка
    WAITING = "waiting"  # Нужен отклик
    MATERIALS = "materials"  # Ждём материалы
    REVIEW = "review"  # Рассмотрена
    APPROVED = "approved"  # Принята
    DISAPPROVED = "disapproved"  # Отклонена


@dataclass(slots=True, frozen=True)
class Request:
    id: int
    topic_id: int
    voting_number: int | None
    voting_title: str | None
    status: RequestStatus


@dataclass(slots=True, frozen=True)
class RequestValueDTO:
    request_id: int
    title: str
    type: ValueType
    value: str | None
