from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import DialogManager
from dishka import FromDishka
from dishka.integrations.aiogram import inject

from fanfan.application.quest.get_user_quest_status import GetUserQuestStatus
from fanfan.core.dto.user import FullUserDTO
from fanfan.core.exceptions.base import AccessDenied
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.filters.commands import QUEST_CMD

quest_handlers_router = Router(name="quest_handlers_router")


@quest_handlers_router.message(Command(QUEST_CMD))
@inject
async def quest_cmd(
    message: Message,
    dialog_manager: DialogManager,
    current_user: FullUserDTO,
    get_user_quest_status: FromDishka[GetUserQuestStatus],
) -> None:
    quest_status = await get_user_quest_status(current_user.id)
    if quest_status.can_participate_in_quest:
        await dialog_manager.start(states.Quest.MAIN)
    else:
        raise AccessDenied(quest_status.reason)
