from typing import Dict

from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.common import WhenCondition
from aiogram_dialog.widgets.text import Text
from aiogram_dialog.widgets.text.format import _FormatDataStub

DELETE_BUTTON = InlineKeyboardBuilder().add(
    InlineKeyboardButton(text="👀 Прочитано", callback_data="delete")
)


class Title(Text):
    def __init__(self, text: str, when: WhenCondition = None):
        super().__init__(when=when)
        self.text = text

    async def _render_text(
        self,
        data: Dict,
        manager: DialogManager,
    ) -> str:
        return f"<b>{self.text.upper()}</b>\n"


class FormatTitle(Text):
    def __init__(self, text: str, when: WhenCondition = None):
        super().__init__(when=when)
        self.text = text

    async def _render_text(
        self,
        data: Dict,
        manager: DialogManager,
    ) -> str:
        if manager.is_preview():
            return self.text.format_map(_FormatDataStub(data=data))
        return f"<b>{self.text.format_map(data).upper()}</b>\n"
