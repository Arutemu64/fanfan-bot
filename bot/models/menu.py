from pathlib import Path
from typing import Optional

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InlineKeyboardMarkup, InputMediaPhoto, Message

from bot import mediacache


class Menu:
    def __init__(
        self,
        title: Optional[str] = None,
        text: str = "%text",
        bottom: Optional[str] = None,
        image: Optional[Path] = None,
        keyboard: Optional[InlineKeyboardMarkup] = None,
        formatting: bool = True,
    ):
        self.title = title
        self.text = text
        self.bottom = bottom
        self.image = image
        self.keyboard = keyboard
        self.formatting = formatting

    def prepare_text(self):
        final_text = ""
        if self.title:
            if self.formatting:
                self.title = f"<b>{self.title}</b>"
            final_text = f"{self.title}\n\n"
        final_text = f"{final_text}{self.text}"
        if self.bottom:
            if self.formatting:
                self.bottom = f"<i>{self.bottom}</i>"
            final_text = f"{final_text}\n\n{self.bottom}"
        return final_text

    async def show(self, message: Message):
        text = self.prepare_text()
        if self.image:
            media = await mediacache.get_media(self.image)
            if message.photo:
                media = InputMediaPhoto(media=media, caption=text)
                edited_msg = await message.edit_media(
                    media=media, reply_markup=self.keyboard
                )
                if edited_msg:
                    await mediacache.set_media_id(
                        self.image, edited_msg.photo[-1].file_id
                    )
            else:
                edited_msg = await message.answer_photo(
                    photo=media, caption=text, reply_markup=self.keyboard
                )
                if edited_msg:
                    await mediacache.set_media_id(
                        self.image, edited_msg.photo[-1].file_id
                    )
                    await message.delete()

        else:
            if message.photo:
                delete = await message.answer(text=text, reply_markup=self.keyboard)
                if delete:
                    await message.delete()
            else:
                try:
                    await message.edit_text(text=text, reply_markup=self.keyboard)
                except TelegramBadRequest:
                    return
        return
