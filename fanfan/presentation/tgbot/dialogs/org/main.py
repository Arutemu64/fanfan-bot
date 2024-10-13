from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Cancel, Start, SwitchTo, Url
from aiogram_dialog.widgets.text import Case, Const, Format
from dishka import AsyncContainer

from fanfan.application.settings.get_settings import GetSettings
from fanfan.application.settings.update_settings import (
    UpdateSettings,
    UpdateSettingsDTO,
)
from fanfan.core.exceptions.base import AppException
from fanfan.infrastructure.auth.utils.token import JwtTokenProcessor
from fanfan.infrastructure.config_reader import WebConfig
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.ui import strings

ID_TOGGLE_VOTING_BUTTON = "id_toggle_voting_button"


async def org_main_getter(
    dialog_manager: DialogManager,
    container: AsyncContainer,
    **kwargs,
):
    web_config: WebConfig = await container.get(WebConfig)
    token_processor: JwtTokenProcessor = await container.get(JwtTokenProcessor)
    get_settings: GetSettings = await container.get(GetSettings)

    settings = await get_settings()
    jwt_token = token_processor.create_access_token(dialog_manager.event.from_user.id)
    return {
        "web_panel_login_link": web_config.build_admin_auth_url(jwt_token),
        "voting_enabled": settings.voting_enabled,
    }


async def toggle_voting_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    container: AsyncContainer = manager.middleware_data["container"]
    get_settings: GetSettings = await container.get(GetSettings)
    update_settings: UpdateSettings = await container.get(UpdateSettings)

    try:
        settings = await get_settings()
        await update_settings(
            UpdateSettingsDTO(voting_enabled=not settings.voting_enabled),
        )
    except AppException as e:
        await callback.answer(e.message)
        return


org_main_window = Window(
    Title(Const(strings.titles.org_menu)),
    Url(
        text=Const("🌐 Перейти в панель организатора"),
        url=Format("{web_panel_login_link}"),
    ),
    Url(
        text=Const(strings.buttons.help_page),
        url=Const("https://fan-fan.notion.site/7234cca8ae1943b18a5bc4435342fffe"),
    ),
    Start(
        state=states.Mailing.main,
        id="new_notification",
        text=Const("✉️ Рассылки"),
    ),
    Start(
        state=states.UserManager.manual_user_search,
        id="user_search",
        text=Const("🔍 Найти пользователя"),
    ),
    SwitchTo(
        state=states.Org.add_ticket,
        id="new_ticket",
        text=Const("🎫 Добавить новый билет"),
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
    Cancel(Const(strings.buttons.back)),
    state=states.Org.main,
    getter=org_main_getter,
)
