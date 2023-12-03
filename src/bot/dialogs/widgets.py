from typing import Dict, Optional

from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.common import WhenCondition
from aiogram_dialog.widgets.text import Text

DELETE_BUTTON = InlineKeyboardBuilder().add(
    InlineKeyboardButton(text="👀 Прочитано", callback_data="delete")
)


class Title(Text):
    def __init__(
        self,
        text: Text,
        when: WhenCondition = None,
        upper: bool = True,
        subtitle: Optional[Text] = None,
    ):
        super().__init__(when=when)
        self.text = text
        self.upper = upper
        self.subtitle = subtitle

    async def _render_text(
        self,
        data: Dict,
        manager: DialogManager,
    ) -> str:
        title = await self.text.render_text(data, manager)
        if self.upper:
            title = title.upper()
        title = f"<b>{title}</b>"
        if self.subtitle:
            title += f"\n<i>{await self.subtitle.render_text(data, manager)}</i>"
        return f"{title}\n"
