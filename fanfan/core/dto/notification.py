from dataclasses import dataclass

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from fanfan.presentation.tgbot.keyboards.buttons import PULL_DOWN_DIALOG

DEFAULT_REPLY_MARKUP = InlineKeyboardBuilder(
    [[PULL_DOWN_DIALOG]],
).as_markup()


@dataclass(slots=True, frozen=True, kw_only=True)
class UserNotification:
    image_id: str | None = None
    title: str | None = "📢 УВЕДОМЛЕНИЕ"
    text: str
    bottom_text: str | None = None
    reply_markup: InlineKeyboardMarkup = DEFAULT_REPLY_MARKUP

    def render_message_text(self) -> str:
        final_text = ""
        if self.title:
            final_text += f"<b>{self.title.upper()}</b>\n\n"
        final_text += self.text
        if self.bottom_text:
            final_text += f"\n\n<i>{self.bottom_text}</i>"
        return final_text
