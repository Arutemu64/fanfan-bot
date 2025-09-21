from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import Cancel, SwitchTo
from aiogram_dialog.widgets.text import Const, Jinja
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from fanfan.adapters.config.models import EnvConfig
from fanfan.core.dto.user import FullUserDTO
from fanfan.core.vo.user import UserRole
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.getters import (
    current_user_getter,
)
from fanfan.presentation.tgbot.dialogs.common.predicates import is_org
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.static import strings


@inject
async def current_user_info_getter(
    dialog_manager: DialogManager,
    current_user: FullUserDTO,
    config: FromDishka[EnvConfig],
    **kwargs,
):
    return {
        # Special setting visibility
        "can_access_dev_settings": config.debug.test_mode
        and current_user.role in [UserRole.HELPER, UserRole.ORG],
    }


settings_main_window = Window(
    Title(Const(strings.titles.settings)),
    Const(
        "ℹ️ В этом разделе ты можешь изменить некоторые настройки, "
        "связанные со своим профилем или заданной ролью."
    ),
    Const(" "),
    Jinja(
        "<b>👤 Никнейм:</b> {% if current_user_username %}"
        "@{{ current_user_username|e }}"
        "{% else %}"
        "не задан"
        "{% endif %}"
    ),
    Jinja("<b>🆔 ID:</b> <code>{{ current_user_id }}</code>"),
    Jinja(
        "<b>🎫 Билет:</b> <code>{{ current_user_ticket_id or 'не привязан' }}</code>"
    ),
    Jinja("<b>🧩 Роль:</b> {{ current_user_role }}"),
    SwitchTo(
        text=Const(strings.titles.user_settings),
        id="open_user_settings",
        state=states.Settings.USER_SETTINGS,
    ),
    SwitchTo(
        text=Const(strings.titles.org_settings),
        state=states.Settings.ORG_SETTINGS,
        id="open_org_settings",
        when=is_org,
    ),
    SwitchTo(
        text=Const(strings.titles.fest_settings),
        id="open_fest_settings",
        state=states.Settings.FEST_SETTINGS,
        when=is_org,
    ),
    SwitchTo(
        text=Const(strings.titles.dev_settings),
        id="open_test_mode",
        state=states.Settings.DEV_SETTINGS,
        when="can_access_dev_settings",
    ),
    Cancel(Const(strings.buttons.back)),
    state=states.Settings.MAIN,
    getter=[current_user_getter],
)
