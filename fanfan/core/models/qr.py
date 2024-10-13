import enum
from dataclasses import dataclass


class QRType(enum.StrEnum):
    ACHIEVEMENT = "achievement"
    USER = "user"


@dataclass(frozen=True, slots=True)
class QR:
    type: QRType
    data: str
