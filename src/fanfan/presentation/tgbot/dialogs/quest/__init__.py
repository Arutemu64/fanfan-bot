from aiogram_dialog import Dialog

from fanfan.presentation.tgbot.dialogs.quest.list_rating import rating_window
from fanfan.presentation.tgbot.dialogs.quest.main import (
    main_quest_window,
)

quest_dialog = Dialog(main_quest_window, rating_window)
