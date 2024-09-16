from aiogram.types import InlineKeyboardButton
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.common import WhenCondition
from aiogram_dialog.widgets.kbd import SwitchInlineQuery
from aiogram_dialog.widgets.text import Text


class Title(Text):
    def __init__(
        self,
        text: Text,
        *,
        when: WhenCondition = None,
        upper: bool = True,
        subtitle: Text | None = None,
    ) -> None:
        super().__init__(when=when)
        self.text = text
        self.upper = upper
        self.subtitle = subtitle

    async def _render_text(
        self,
        data: dict,
        manager: DialogManager,
    ) -> str:
        title = await self.text.render_text(data, manager)
        if self.upper:
            title = title.upper()
        title = f"<b>{title}</b>"
        if self.subtitle:
            title += f"\n<i>{await self.subtitle.render_text(data, manager)}</i>"
        return f"{title}\n"


class SwitchInlineQueryCurrentChat(SwitchInlineQuery):
    async def _render_keyboard(
        self,
        data: dict,
        manager: DialogManager,
    ) -> list[list[InlineKeyboardButton]]:
        return [
            [
                InlineKeyboardButton(
                    text=await self.text.render_text(data, manager),
                    switch_inline_query_current_chat=await self.switch_inline.render_text(  # noqa: E501
                        data,
                        manager,
                    ),
                ),
            ],
        ]
