from dataclasses import dataclass

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from pydantic import BaseModel

from fanfan.core.models.user import UserId
from fanfan.presentation.tgbot.keyboards.buttons import PULL_DOWN_DIALOG


@dataclass(frozen=True, slots=True)
class UserNotification:
    text: str
    title: str = "📢 УВЕДОМЛЕНИЕ"
    bottom_text: str | None = None
    image_id: str | None = None
    reply_markup: InlineKeyboardMarkup = InlineKeyboardBuilder(
        [[PULL_DOWN_DIALOG]],
    ).as_markup()

    def render_message_text(self) -> str:
        title = f"<b>{self.title.upper()}</b>"
        text = f"{title}\n\n{self.text}"
        if self.bottom_text:
            text = f"{text}\n\n<i>{self.bottom_text}</i>"
        return text


class SendNotificationDTO(BaseModel):
    user_id: UserId
    notification: UserNotification
