import enum
from dataclasses import dataclass


class QRType(enum.StrEnum):
    ACHIEVEMENT = enum.auto()
    USER = enum.auto()


@dataclass(slots=True, kw_only=True, frozen=True)
class QR:
    type: QRType
    data: str
