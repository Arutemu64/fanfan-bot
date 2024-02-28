from dataclasses import dataclass
from datetime import datetime
from typing import Generic, List, Optional, TypeVar

from fanfan.common.enums import QRCommand

AbstractModel = TypeVar("AbstractModel")


@dataclass
class Page(Generic[AbstractModel]):
    items: List[AbstractModel]
    number: int
    total: int


@dataclass(kw_only=True)
class UserNotification:
    user_id: int
    text: str
    title: str = "📢 УВЕДОМЛЕНИЕ"
    bottom_text: Optional[str] = None
    image_id: Optional[str] = None
    timestamp: Optional[datetime] = None

    def render_message_text(self) -> str:
        title = self.title.upper()
        if self.timestamp:
            title = f"{title} ({self.timestamp.strftime('%H:%M')})"
        title = f"<b>{title}</b>"
        text = f"{title}\n\n{self.text}"
        if self.bottom_text:
            text = f"{text}\n\n<i>{self.bottom_text}</i>"
        return text


@dataclass
class QR:
    command: QRCommand
    parameter: str

    @classmethod
    def parse(cls, qr_text: str):
        return cls(command=QRCommand(qr_text.split()[0]), parameter=qr_text.split()[1])

    def __repr__(self):
        return f"{self.command} {self.parameter}"
