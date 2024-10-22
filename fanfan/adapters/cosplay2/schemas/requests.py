import enum
from dataclasses import dataclass


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
    voting_title: str | None
    status: RequestStatus
