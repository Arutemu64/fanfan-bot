from aiogram_dialog import Dialog

from fanfan.presentation.tgbot.dialogs.quest.cancel_registration import (
    cancel_registration_window,
)
from fanfan.presentation.tgbot.dialogs.quest.main import (
    main_quest_window,
)

dialog = Dialog(main_quest_window, cancel_registration_window)
