from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import Cancel, SwitchTo
from aiogram_dialog.widgets.text import Const, Jinja
from dishka import AsyncContainer

from fanfan.adapters.config.models import EnvConfig
from fanfan.core.models.user import UserData
from fanfan.core.vo.user import UserRole
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.predicates import is_org
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.static import strings


async def current_user_info_getter(
    dialog_manager: DialogManager,
    user: UserData,
    container: AsyncContainer,
    **kwargs,
):
    config: EnvConfig = await container.get(EnvConfig)
    return {
        "user_id": user.id,
        "username": user.username,
        "ticket_id": user.ticket.id if user.ticket else None,
        "role": user.role,
        # Special setting visibility
        "can_access_dev_settings": config.debug.test_mode
        and user.role in [UserRole.HELPER, UserRole.ORG],
    }


settings_main_window = Window(
    Title(Const(strings.titles.settings)),
    Const(
        "ℹ️ В этом разделе ты можешь изменить некоторые настройки, "
        "связанные со своим профилем или заданной ролью."
    ),
    Const(" "),
    Jinja(
        "<b>👤 Никнейм:</b> {% if username %}"
        "@{{ username|e }}"
        "{% else %}"
        "не задан"
        "{% endif %}"
    ),
    Jinja("<b>🆔 ID:</b> <code>{{ user_id }}</code>"),
    Jinja(
        "<b>🎫 Билет:</b> {% if ticket_id %}"
        "<code>{{ ticket_id }}</code>"
        "{% else %}"
        "не привязан"
        "{% endif %}"
    ),
    Jinja("<b>🧩 Роль:</b> {{ role }}"),
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
    getter=current_user_info_getter,
)
