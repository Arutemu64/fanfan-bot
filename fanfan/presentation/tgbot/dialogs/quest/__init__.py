from aiogram_dialog import Dialog

from fanfan.presentation.tgbot.dialogs.quest.main import (
    main_quest_window,
)
from fanfan.presentation.tgbot.dialogs.quest.rating import rating_window

dialog = Dialog(main_quest_window, rating_window)
