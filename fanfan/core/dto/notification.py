from dataclasses import dataclass

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from fanfan.presentation.tgbot.keyboards.buttons import PULL_DOWN_DIALOG

DEFAULT_REPLY_MARKUP = InlineKeyboardBuilder(
    [[PULL_DOWN_DIALOG]],
).as_markup()


@dataclass(slots=True, frozen=True)
class UserNotification:
    text: str
    title: str = "📢 УВЕДОМЛЕНИЕ"
    bottom_text: str | None = None
    image_id: str | None = None
    reply_markup: InlineKeyboardMarkup = DEFAULT_REPLY_MARKUP

    def render_message_text(self) -> str:
        title = f"<b>{self.title.upper()}</b>"
        text = f"{title}\n\n{self.text}"
        if self.bottom_text:
            text = f"{text}\n\n<i>{self.bottom_text}</i>"
        return text
