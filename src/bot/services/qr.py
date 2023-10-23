from typing import Optional

from aiogram import Bot
from aiogram.types import Message
from aiogram_dialog import BaseDialogManager, DialogManager

from src.bot.dialogs import states
from src.bot.ui import strings
from src.db import Database


async def proceed_qr_code(
    manager: DialogManager | BaseDialogManager,
    db: Database,
    qr_text: str,
    message: Message = None,
    user_id: Optional[int] = None,
    bot: Bot = None,
):
    match qr_text.split()[0]:
        case "user":
            if qr_text.split()[1].isnumeric():
                if await db.user.get(int(qr_text.split()[1])):
                    await manager.start(
                        state=states.USER_MANAGER.MAIN,
                        data=int(qr_text.split()[1]),
                    )
                else:
                    if message:
                        await message.answer(strings.errors.user_not_found)
                    elif bot and user_id:
                        await bot.send_message(
                            chat_id=user_id, text=strings.errors.user_not_found
                        )
