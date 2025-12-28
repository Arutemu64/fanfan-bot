from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import DialogManager

from fanfan.core.dto.user import FullUserDTO
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.filters.commands import LINK_TICKET_CMD

link_ticket_handlers_router = Router(name="link_ticket_handlers_router")


@link_ticket_handlers_router.message(Command(LINK_TICKET_CMD))
async def link_ticket_cmd(
    message: Message,
    dialog_manager: DialogManager,
    current_user: FullUserDTO,
) -> None:
    if current_user.ticket is None:
        await dialog_manager.start(states.LinkTicket.MAIN)
