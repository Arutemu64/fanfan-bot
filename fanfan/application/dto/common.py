from dataclasses import dataclass
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
    image_id: Optional[int] = None
    delete_after: Optional[int] = None

    def render_message_text(self) -> str:
        text = f"<b>{self.title.upper()}</b>\n\n{self.text}"
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
