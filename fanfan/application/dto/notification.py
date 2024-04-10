from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True, slots=True)
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


@dataclass(frozen=True, slots=True)
class DeliveryInfo:
    delivery_id: str
    count: int
