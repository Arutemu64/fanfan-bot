from aiogram import Bot
from aiogram_dialog import BaseDialogManager

from src.bot.dialogs import states
from src.bot.structures import QR, QRCommand
from src.bot.ui import strings
from src.db import Database
from src.db.models import User


async def open_user_manager(user: User, manager: BaseDialogManager) -> None:
    await manager.start(state=states.USER_MANAGER.MAIN, data=user.id)


async def proceed_qr_code(
    qr: QR,
    bot: Bot,
    manager: BaseDialogManager,
    db: Database,
    user_id: int,
) -> None:
    match qr.command:
        case QRCommand.USER:
            user = await db.user.get(int(qr.parameter))
            if user:
                await open_user_manager(user, manager)
            else:
                await bot.send_message(
                    chat_id=user_id, text=strings.errors.user_not_found
                )
