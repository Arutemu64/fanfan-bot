from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Cancel, Group, Start, SwitchTo, Url
from aiogram_dialog.widgets.text import Case, Const, Format
from dishka import AsyncContainer

from fanfan.adapters.auth.utils.token import JwtTokenProcessor
from fanfan.adapters.config.models import Configuration
from fanfan.application.settings.get_settings import GetSettings
from fanfan.application.settings.update_settings import (
    UpdateSettings,
    UpdateSettingsDTO,
)
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.static import strings

ID_TOGGLE_VOTING_BUTTON = "id_toggle_voting_button"


async def org_main_getter(
    dialog_manager: DialogManager,
    container: AsyncContainer,
    **kwargs,
):
    config: Configuration = await container.get(Configuration)
    token_processor: JwtTokenProcessor = await container.get(JwtTokenProcessor)
    get_settings: GetSettings = await container.get(GetSettings)

    settings = await get_settings()
    jwt_token = token_processor.create_access_token(dialog_manager.event.from_user.id)
    return {
        "admin_auth_url": config.web.build_admin_auth_url(jwt_token),
        "voting_enabled": settings.voting_enabled,
        "docs_link": config.docs_link,
    }


async def toggle_voting_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    container: AsyncContainer = manager.middleware_data["container"]
    get_settings: GetSettings = await container.get(GetSettings)
    update_settings: UpdateSettings = await container.get(UpdateSettings)

    settings = await get_settings()
    await update_settings(
        UpdateSettingsDTO(voting_enabled=not settings.voting_enabled),
    )


org_main_window = Window(
    Title(Const(strings.titles.org_menu)),
    Group(
        Url(
            text=Const("🌐 Орг-панель"),
            url=Format("{admin_auth_url}"),
            when="admin_auth_url",
        ),
        Url(
            text=Const(strings.buttons.help_page),
            url=Format("{docs_link}"),
            when="docs_link",
        ),
        Start(
            state=states.Mailing.main,
            id="new_notification",
            text=Const("✉️ Рассылки"),
        ),
        Start(
            state=states.UserManager.manual_user_search,
            id="user_search",
            text=Const("🔍 Поиск пользователей"),
        ),
        SwitchTo(
            state=states.Org.add_ticket,
            id="new_ticket",
            text=Const("🎫 Новый билет"),
        ),
        Button(
            Case(
                {
                    True: Const("🔴 Выключить голосование"),
                    False: Const("🟢 Включить голосование"),
                },
                selector="voting_enabled",
            ),
            id=ID_TOGGLE_VOTING_BUTTON,
            on_click=toggle_voting_handler,
        ),
        SwitchTo(
            Const(strings.titles.tasks),
            id="tasks",
            state=states.Org.tasks,
        ),
        width=2,
    ),
    Cancel(Const(strings.buttons.back)),
    state=states.Org.main,
    getter=org_main_getter,
)
