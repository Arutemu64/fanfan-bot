from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, SwitchTo
from aiogram_dialog.widgets.text import Case, Const
from dishka import AsyncContainer

from fanfan.application.settings.get_settings import GetSettings
from fanfan.application.settings.update_settings import UpdateSettings
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.static import strings

ID_TOGGLE_VOTING_BUTTON = "id_toggle_voting_button"


async def fest_settings_getter(
    dialog_manager: DialogManager,
    container: AsyncContainer,
    **kwargs,
):
    get_settings: GetSettings = await container.get(GetSettings)
    settings = await get_settings()
    return {
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

    settings = await get_settings()
    await update_settings.toggle_voting(voting_enabled=not settings.voting_enabled)


fest_settings_window = Window(
    Title(Const(strings.titles.fest_settings)),
    Button(
        Case(
            {
                True: Const("📣 Голосование: ✅"),
                False: Const("📣 Голосование: ❌"),
            },
            selector="voting_enabled",
        ),
        id=ID_TOGGLE_VOTING_BUTTON,
        on_click=toggle_voting_handler,
    ),
    SwitchTo(Const(strings.buttons.back), state=states.Settings.MAIN, id="back"),
    state=states.Settings.FEST_SETTINGS,
    getter=fest_settings_getter,
)
