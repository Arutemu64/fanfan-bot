from aiogram import Router
from aiogram_dialog import Dialog

from fanfan.presentation.tgbot.dialogs.quest.handlers import quest_handlers_router
from fanfan.presentation.tgbot.dialogs.quest.list_rating import rating_window
from fanfan.presentation.tgbot.dialogs.quest.main import (
    main_quest_window,
)

quest_router = Router(name="quest_router")

quest_dialog = Dialog(main_quest_window, rating_window)

quest_router.include_routers(quest_handlers_router, quest_dialog)
